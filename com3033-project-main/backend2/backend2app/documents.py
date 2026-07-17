from django_elasticsearch_dsl import Document, fields, Date
from django_elasticsearch_dsl.registries import registry
from backend2app.models import JobSearch
from elasticsearch_dsl.analysis import analyzer, tokenizer

# Used to break the searchable text in the database into words of min of 4 chars, max of 10 chars
# (For example, if the word is "tests", the ngrams will be ["test", "ests", "tests"])
ngram_tokenizer = tokenizer(
    'ngram_tokenizer',
    type='ngram',
    min_gram=4,
    max_gram=10,
    token_chars=['letter', 'digit']

)

ngram_analyzer = analyzer(
    'ngram_analyzer',
    tokenizer=ngram_tokenizer,
    filter=['lowercase']
)

# If the user searches something that appearing in the ngrams of an entry, that entry will appear in the search results


@registry.register_document
class JobSearchDocument(Document):
    company_name = fields.TextField(
        analyzer=ngram_analyzer, search_analyzer=ngram_analyzer)
    alt_description = fields.TextField(
        analyzer=ngram_analyzer, search_analyzer=ngram_analyzer)
    job_selection = fields.TextField(
        analyzer=ngram_analyzer,
        search_analyzer=ngram_analyzer,
        fields={
            "raw": fields.KeywordField()
        }
    )
    period_end = fields.DateField()

    class Index:
        name = 'jobssearch'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'index': {
                'max_ngram_diff': 8
            },
            'analysis': {
                'tokenizer': {
                    'ngram_tokenizer': {
                        'type': 'ngram',
                        'min_gram': 4,
                        'max_gram': 10,
                        'token_chars': ['letter', 'digit']

                    }
                },
                'analyzer': {
                    'ngram_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'ngram_tokenizer',
                        'filter': ['lowercase']
                    }
                }
            }
        }

    class Django:
        model = JobSearch
        fields = ['job_id', 'comp_stage', 'practice_id']
