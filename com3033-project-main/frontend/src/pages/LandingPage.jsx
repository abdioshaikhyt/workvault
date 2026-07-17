import React from "react";
function LandingPage() {
  return (
  <div>
    <div style={{display: 'flex', alignItems: 'flex-start', gap: '15px'}}>
      <pre style={{
        fontFamily: 'Courier New, monospace',
        fontSize: '7px',
        lineHeight: 1,
        margin: 0
      }}>
{`###################
######## ▲ ########
####### / \\ #######
###### /   \\ ######
##### /     \\ #####
#### ^       ^ ####
### /  \\   /  \\ ###
## /    \\ /    \\ ##
# /      -      \\ #
###################
###################`}
      </pre>
      <div>
        <h1>Welcome to Work Vault!</h1>
        <a href="/login">Login</a>&nbsp;&nbsp;&nbsp;&nbsp;<a href="/register">Sign up</a>
      </div>
    </div>

    <p>{"WorkVault revolutionizes tax practices with its powerful web-based workflow management and secure document storage platform, tailored for accountancy firms and tax practitioners."}</p>
    <p>{"Take advantage of:"}</p>
    <ul>
      <li><strong>Real-time dashboard</strong> for instant visibility into every job</li>
      <li><strong>Job workflows</strong> that seamlessly connect your tax team</li>
      <li><strong>Document version control</strong> to track changes effortlessly</li>
    </ul>
    
    <p>{"Ignite your firm's productivity, slash administrative headaches, and deliver exceptional results faster than ever before."}</p>
    <p>
      <strong>Contact us today</strong> for personalized pricing and 
      seamless onboarding at <a href="mailto:workvaultcontact.gmail.com">workvaultcontact@gmail.com</a>.
    </p>

  </div>
);
};

export default LandingPage;
