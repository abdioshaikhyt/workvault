from django.http import HttpResponse
import abc
import asyncpg
import asyncio
from rest_framework.views import APIView
from rest_framework.response import Response
from elasticsearch_dsl import Q
from .documents import JobSearchDocument
from .serializers import JobSearchDocumentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework import status
from rest_framework.response import Response
import random
from contextlib import asynccontextmanager
from django.conf import settings
from asgiref.sync import async_to_sync, sync_to_async
from .models import LogoutAccessToken
from rest_framework.permissions import AllowAny
from rest_framework.pagination import LimitOffsetPagination


async_pool = None


async def get_pool():
    # Creates a pool for asynchronous execution for database queries with a constant connection rather than reconnecting for each request
    global async_pool
    if async_pool is None:
        async_pool = await asyncpg.create_pool(
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            database=settings.DATABASES['default']['NAME'],
            host=settings.DATABASES['default']['HOST'],
            max_size=20,
        )
    return async_pool

# If too many requests are sent to the database at once, it will not be able to answer all of them.
# This retry logic allows the request to retry a number of time before returning an error


@asynccontextmanager
async def acquire_connection_with_retry(pool, max_retries=5, base_delay=0.1):
    delay = base_delay
    connection = None
    try:
        for attempt in range(max_retries):
            try:
                connection = await pool.acquire()
                break
            except (asyncpg.exceptions.TooManyConnectionsError, ConnectionError) as e:
                if attempt == max_retries - 1:
                    raise
                jitter = random.uniform(0, 0.1)
                await asyncio.sleep(delay + jitter)
                delay *= 2
        yield connection
    finally:
        if connection:
            await pool.release(connection)

# Checks to see if a token is in the table storing auth tokens that have been used but not expired yet
# (These are invalid, they are tokens for users that have logged out and are stored until expiry)


async def is_token_blacklisted(token: str) -> bool:
    pool = await get_pool()
    async with acquire_connection_with_retry(pool) as connection:
        async with connection.transaction():
            row = await connection.fetchrow(
                "SELECT 1 FROM backend2app_logoutaccesstoken WHERE token = $1 LIMIT 1",
                token
            )
            return row is not None


class ElasticSearchAPIView(APIView, LimitOffsetPagination):
    serializer_class = None
    document_class = None
    permission_classes = [IsAuthenticated]

    # Defines an abstract method to be overridden for writing queries with Q expressions
    @abc.abstractmethod
    def generate_q_expression(self, query):
        """This method should be overridden and return a Q() expression."""

    # Redirects searches to be asynchronous
    def get(self, request):
        query = request.GET.get('q', '')
        return async_to_sync(self.async_get)(request, query)

    async def async_get(self, request, query):

        auth_header = request.headers.get('Authorization')

        # Checks to see if the request has an auth token attached
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'No access token provided.'}, status=status.HTTP_400_BAD_REQUEST)
        token = auth_header.split('Bearer ')[1]

        # Checks to see if the auth token is invalid
        if await is_token_blacklisted(token):
            return Response({'detail': 'This token has been logged out.'}, status=status.HTTP_401_UNAUTHORIZED)

        auth = JWTStatelessUserAuthentication()
        raw_token = auth.get_raw_token(auth.get_header(request))

        # Checks to see if the auth token is one that has access to the page/that it exists
        if raw_token is None:
            return Response({"detail": "Authorization header missing or invalid"},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            validated_token = auth.get_validated_token(raw_token)
        except InvalidToken:
            return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        # Tries to get the practice_id (id of the practice that the job belongs to) from the auth token to check if it exists.
        # If this does not succeed, returns blank dummy data
        jwt_practice_id = validated_token.payload.get('practice_id')
        if not jwt_practice_id:
            return Response({
                "count": 0,
                "Next": None,
                "Previous": None,
                "results": []
            })

        try:
            # Creates a q expression using the query and the previously aqquired practice_id
            q = self.generate_q_expression(query, practice_id=jwt_practice_id)

            # Creates the offsets and limits for pagination of results
            offset = self.get_offset(request) or 0
            limit = self.get_limit(request) or 10
            self.offset = int(offset)
            self.limit = int(limit)

            # Searches with the query and selects the objects from offset to offset+limit from the results
            # (If gets 20 results, offset is 10 and limit is 10 it would return results 10 to 19 inclusive since index from 0)
            search = self.document_class.search().query(q)[offset:offset+limit]
            response = search.execute()
            total_hits = response.hits.total.value if hasattr(
                response.hits.total, 'value') else response.hits.total

            # Creates a list of the responses to be displayed
            hits = [hit for hit in response.hits]
            serializer = self.serializer_class(hits, many=True)

            # Used to create urls based on the offset
            def build_url(offset):
                base = request.build_absolute_uri(request.path)
                qparams = request.GET.copy()
                qparams['offset'] = offset
                url = f"{base}?{qparams.urlencode()}"
                return url

            next_offset, previous_offset, next_url, previous_url = None, None, None, None
            # Determines if there are enough results to need multiple pages of results
            if (offset + limit) < total_hits:
                next_offset = offset + limit
                next_url = build_url(next_offset)

            # Determines if there was a previous page of results
            if (offset - limit) >= 0:
                previous_offset = offset - limit
                previous_url = build_url(previous_offset)

            # Returns the search results, number of results total and any related URLs for pagination
            return Response({
                "count": total_hits,
                "next": next_url,
                "previous": previous_url,
                "results": serializer.data,
            })
        except Exception as e:
            return HttpResponse(e, status=500)


class JobSearchAPIView(ElasticSearchAPIView):
    serializer_class = JobSearchDocumentSerializer
    document_class = JobSearchDocument

    def generate_q_expression(self, query, practice_id=None):
        # Ensures the query isn't case sensitive
        lower_query = query.lower()
        upper_query = query.upper()
        # Creates a query using 5 Q expressions (4 for the upper and lower cases of job_selection and company_name, 1 for an exact match to the strings)
        # to ensure the data is found if it exists
        base_query = Q(
            "bool",
            should=[
                Q("multi_match",
                  query=query,
                  fields=["company_name", "alt_description", "job_selection"],
                  fuzziness="auto",
                  prefix_length=1,
                  max_expansions=50),

                Q("term", **{"job_selection.raw": lower_query}),
                Q("term", **{"job_selection.raw": upper_query}),
                Q("term", **{"company_name.raw": lower_query}),
                Q("term", **{"company_name.raw": upper_query}),
            ],
            minimum_should_match=1,
        )
        # If practice_id exists, use it to create another query to filter results to just that practice
        if practice_id:
            practice_filter = Q("term", practice_id=practice_id)
            return base_query & practice_filter
        return base_query


class LogoutAndStoreTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return async_to_sync(self.async_get)(request)

    async def async_get(self, request):
        auth_header = request.headers.get('Authorization')
        # Checks to see if a token is attached to the request
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'No access token provided.'}, status=status.HTTP_400_BAD_REQUEST)

        token = auth_header.split('Bearer ')[1]

        # Creates a LogoutAccessToken object for the given token, blacklisting it
        await LogoutAccessToken.objects.acreate(token=token)

        return Response({'detail': 'Access token stored successfully.'}, status=status.HTTP_200_OK)
