# The Fidelius Charm - Keeping Things Secret

Fidelius is a package for fetching (and managing) secrets and other 
parameters from AWS' Parameter Store.

This is designed with CCP Borg Application Framework and the Alviss config 
package in mind but should work for other cases as well.

**IMPORTANT:** This has been migrated more-or-less _"as-is"_ from CCP Tool's 
internal repo and hasn't yet been given the love it needs to be properly 
open-sourced and user friendly for other people _(unless you read though the 
code and find it perfectly fits your use case)_. 

## What should be stored with Fidelius

All secrets, always, as Secret Parameters (they are stored as encrypted)!

This includes (but is not limited to):

- Passwords of any kind
- Secret/Access Keys
- API Tokens
- Shared Secrets (e.g. JWT secrets)
- Encryption keys and/or salts
- ...basically any credentials or stuff that needs to remain secret!

Also, it's prudent to store any credentials that are related 
(directly or indirectly) to the secrets stored, e.g.:

- Usernames
- Resource identifiers (DB names and such)
- Hosts / Virtual Hosts
- ...stuff like that!

The reasoning is roughly this; if/when the secrets being stored need to be 
changed or rotated, there is often a need to change other credential related 
things e.g. a username if we're performing a rolling/overlapping rotation 
or a host if changing an API token and pointing to a different URL and so on.

Basically, imagine that someone gets a hold of all of our secrets and we 
need to rotate them as soon as possible, being able to change both a 
password and its username and host from the same place (Fidelius or AWS 
Parameter Store) in a single operation WITHOUT needing to deploy anything 
new or changed is critical and if we need to do this for hundreds of 
services at once, every second counts!


## How to Use / Best Practices

What you'll need first:

- An AWS account
  - Fidelius is designed to work within an AWS environment, fetching secrets 
    and parameters from the Parameter Store of AWS' Systems Manager utility 
    and using the AWS Key Management Service (KMS) for secret 
    encryption/decryption.
- A dedicated key in KMS' for encryption and decryption of secrets
  - Preferably with the alias `fidelius-key` but that's configurable via the 
    `FIDELIUS_AWS_KEY_ARN` environment variable
- A few different service users with different permission policies and their 
  AWS security credentials / access keys
  - One for administrating secrets/parameters
  - One for local development
  - One for your CI/CD system to use (if needed)
  - One for deployed applications to use in runtime


### The Admin User/Policy

To administrate parameters you'll need credentials with the following 
permissions:

- `kms:Decrypt` & `kms:Encrypt`
  - Bind this to the encryption key's ARN, e.g. `arn:aws:kms:eu-west-1:AWS_ACCOUNT_ID:key/fidelius-key`
    - Where `AWS_ACCOUNT_ID` is your AWS account number
    - Change the region as needed
- Everything to do with parameters in the SSM:
  - `ssm:LabelParameterVersion`
  - `ssm:GetParameterHistory`
  - `ssm:GetParameters`
  - `ssm:GetParameter`
  - `ssm:DeleteParameters`
  - `ssm:PutParameter`
  - `ssm:DeleteParameter`
  - `ssm:RemoveTagsFromResource`
  - `ssm:AddTagsToResource`
  - `ssm:ListTagsForResource`
  - `ssm:GetParametersByPath`
  - Bind this to the ARN of the `fidelius` path in the Parameter Store
    - `arn:aws:ssm:eu-west-1:AWS_ACCOUNT_ID:parameter/fidelius/*`
      - Where `AWS_ACCOUNT_ID` is your AWS account number
      - Change the region as needed
- It's also very wise to limit the use of this user/policy to a fixed IP or 
  set of IP address if possible from which you'll be performing admin 
  operations on secrets and parameters

To administrate (create/edit) parameters and secrets set the credentials for 
this account to these environment variables and follow the directions in the 
[Creating Parameters and Secrets Locally](#creating-parameters-and-secrets-locally) chapter.
- `FIDELIUS_AWS_ACCESS_KEY_ID`
- `FIDELIUS_AWS_SECRET_ACCESS_KEY`

**Note**: You can also just give these permissions to your personal AWS 
account and use those credentials if you prefer but having a dedicated 
service account for administrating these is highly recommended.


### The Local Development User/Policy

Local developers will need to fetch dev parameters and secrets for things to 
run so they'll need the following action permissions:

- `kms:Decrypt`
- `ssm:GetParametersByPath`
- `ssm:GetParameters`
- `ssm:GetParameter`

These need to be bound to the encryption key and parameter store ARNs, e.g.:

- `arn:aws:kms:eu-west-1:AWS_ACCOUNT_ID:key/fidelius-key`
- `arn:aws:ssm:eu-west-1:AWS_ACCOUNT_ID:parameter/fidelius/*`
  - Where `AWS_ACCOUNT_ID` is your AWS account number
  - Change the region as needed

**Note**: You can also just give these permissions to developers personal AWS 
account and use those credentials.

**Another Note**: If I remember correctly, then it's also possible to make the 
resource binding on the parameter store path more constricting, e.g. by 
limiting it to an application and/or runtime environment, thus preventing 
production secrets from being accessible by curious developers, like:
`arn:aws:ssm:eu-west-1:AWS_ACCOUNT_ID:parameter/fidelius/*/local/mycoolapp/*`


### The CI/CD User/Policy

This one may not be needed depending on your setup and system but the point 
is that sometimes CI/CD pipelines may need to access parameters and secrets 
in order to run automated unit and/or integration tests.

In that case, just make a service user/policy similar to the Local 
Development one but it's highly recommended to restrict the credentials 
usage to the IP or IP range of the CI/CD system and even to treat testing as 
its own "runtime environment" (like `local`, `test`, `prod`, etc.) and limit 
the parameter store ARN to that as well as either application and/or 
application group:
`arn:aws:ssm:eu-west-1:AWS_ACCOUNT_ID:parameter/fidelius/mygroup/unittest/*`


### The Runtime Application User/Policy

This one is intended for the applications to use in its runtime environment 
(e.g. a Kubernetes Cluster or EC2 machine or whatever) and it should be 
restricted to the IP address or range of that environment, such that even if 
the credentials were to be exposed, they'd be useless unless used from 
within that runtime environment.

Again the permissions needed are just the ability to get parameters and 
decrypt them using the designated key so:

- `kms:Decrypt`
- `ssm:GetParametersByPath`
- `ssm:GetParameters`
- `ssm:GetParameter`

These need to be bound to the encryption key and parameter store ARNs, e.g.:

- `arn:aws:kms:eu-west-1:AWS_ACCOUNT_ID:key/fidelius-key`
- `arn:aws:ssm:eu-west-1:AWS_ACCOUNT_ID:parameter/fidelius/*`
  - Where `AWS_ACCOUNT_ID` is your AWS account number
  - Change the region as needed

**Note**: It's highly recommended to have at least one of these per 
"application group" (e.g. a few microservice applications servicing a single 
business domain) or even one per application, and restricting the parameter 
store ARN to match. 


## Configuration Parameters

Set one of the AWS Secret Credentials from above to the following 
Environmental variables in order to give Fidelius access to what it needs: 

- `FIDELIUS_AWS_ACCESS_KEY_ID`
- `FIDELIUS_AWS_SECRET_ACCESS_KEY`

If these are not present then Fidilius will try and use these instead:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

These should VERY preferably be the ONLY credentials in your project and 
stored in a secure and encrypted way up-until they're needed for deployment 
and such. 

You will also need to supply the ARN of the decryption/encryption key via 
environment variable:

- `FIDELIUS_AWS_KEY_ARN`
  - E.g. `arn:aws:kms:eu-west-1:123456789:alias/fidelius-key'` 

The following Environment Variables can also be set to override the defaults:

- `AWS_DEFAULT_REGION`: This is `eu-west-1` by default in Fidelius and 
  doesn't need to be set.


## Using Fidelius with Alviss

Use the `${__FID__:parameter_name}` expression withing the application config 
files for application specific parameters and 
`$ {__FID__:shared_group_name:parameter_name}` for group shared parameters.

```yaml
app:
  module_name: exampleapp
  slug: example-app  # This is used by Fidelius
  group: mygroup  # This is required now!
  env: prod  # Runtime environment from Environment Var

publisher:
  connection:
    # Application Specific Parameters
    # This will be fetched from:
    # /fidelius/mygroup/prod/apps/example-app/DB_PASSWORD
    # ...or if no "prod" values are found from:
    # /fidelius/mygroup/default/apps/example-app/DB_PASSWORD
    password: ${__FID__:DB_PASSWORD}
    
    # Shared Group Parameters
    # This will be fetched from:
    # /fidelius/mygroup/prod/shared/rabbitmq/DB_PASSWORD
    # ...or if no "prod" values are found from:
    # /fidelius/mygroup/default/shared/rabbitmq/DB_PASSWORD
    host: ${__FID__:rabbitmq:RABBIT_MQ_HOST}
```

## Using Fidelius in Other Applications

For general usage you can use the same expressions as above in any config you 
use and then have Fidelius replace them once you've read them in like so:

```json
{
  "someconfig": {
    "somepassword": "${__FID__:my_cool_password}"
  }
}
```

Then in Python:

```python
from fidelius.fideliusapi import ParameterStore
from fidelius.fideliusapi import fidelius_replace

# Read config from config somehow...
pass_from_conf = read_my_config('somepassword')

# Create the Parameter Store
ps = ParameterStore(app='my_application', 
                    group='my_group',
                    env='test')

# Will read from /fidelius/my_group/test/apps/my_application/my_cool_password
# (...or default)
real_password = fidelius_replace('pass_from_conf', ps)
```

## Using Fidelius Directly

While it makes most sense to use Fidelius to look up values injected from 
configurations you can also just use it directly in code like so:

```python
from fidelius.fideliusapi import ParameterStore

# Create the Parameter Store
ps = ParameterStore(app='my_application', 
                    group='my_group',
                    env='test')

# Will read from /fidelius/my_group/test/apps/my_application/my_cool_password
# (...or default)
real_or_default_password = ps.get('my_cool_password')

# This forcefully skips using the default value:
real_password = ps.get('my_cool_password', no_default=True)

# This fetches from a shared group folder
# Will read from /fidelius/my_group/test/shared/someFolder/shared_password
shared_password = ps.get('shared_password', 'someFolder')
```


## Creating Parameters and Secrets Locally

Set the following Environmental Variables to credentials the [appropriate 
access](#the-admin-userpolicy):

- `FIDELIUS_AWS_ACCESS_KEY_ID`
- `FIDELIUS_AWS_SECRET_ACCESS_KEY`

```python
from fidelius.gateway.paramadmin import *

# Create the Parameter Store Admin
pa = ParameterStoreAdmin(
    app='example-app',  # This is the app slug (not app module name)
    group='mygroup',  # The project group, e.g. "monetization", "px" etc.
    env='default',  # default | dev | test | prod etc.
    owner='batcave',  # The team that owns the applications
)

# Create an application specific parameter
pa.create_param(name='MSG_QUEUE_USERNAME',
                value='svc_username_dev',
                description='Give it a meaningful description')

# This will create the parameter under: 
# /fidelius/mygroup/default/apps/example-app/MSG_QUEUE_USERNAME
```

### And Now A Secret

```python
# Now lets create a secret:
pa.create_secret(name='MSG_QUEUE_USERNAME',
                 value='somekindofpassword',
                 description='Give it a meaningful description')
```

### Override Default Value with Environment Specific Ones

```python
# Now lets create the prod password value that will override the default 
# ones in production...

pa.set_env('prod')  # Change the env to prod instead of default
pa.create_param(name='MSG_QUEUE_USERNAME',
                value='atotallydifferentpassword',
                description='Give it a meaningful description')
```

## Creating Shared Parameters and Secrets Locally

ASet the following Environmental Variables to credentials the [appropriate 
access](#the-admin-userpolicy):

- `FIDELIUS_AWS_ACCESS_KEY_ID`
- `FIDELIUS_AWS_SECRET_ACCESS_KEY`

```python
from fidelius.gateway.paramadmin import *

# Create the Parameter Store Admin
pa = ParameterStoreAdmin(
    app='example-app',  # This isn't used for shared params/secrets
    group='mygroup',  # Shared params/secrets are only shared across a group
    env='default',  # default | dev | test | prod etc.
    owner='batcave',  # The team that owns the group
)

# Create a group shared parameter
pa.create_shared_param(name='RABBIT_MQ_VHOST',
                       folder='rabbitmq',
                       value='rabbitmq-dev.ccptools.cc',
                       description='Give it a meaningful description')

# Create a group shared secret
pa.create_shared_secret(name='RABBIT_MQ_PASSWORD',
                        folder='rabbitmq',
                        value='reallyBadPassword',
                        description='Give it a meaningful description')

# This will create the parameters under: 
# /fidelius/mygroup/default/shared/rabbitmq/RABBIT_MQ_VHOST
# /fidelius/mygroup/default/shared/rabbitmq/RABBIT_MQ_PASSWORD
```

### Override Default Value with Environment Specific Ones

```python
# Now lets create the prod password value that will override the default 
# ones in production...

pa.set_env('prod')  # Change the env to prod instead of default

# Create a group shared parameter for production
pa.create_shared_param(name='RABBIT_MQ_VHOST',
                       folder='rabbitmq',
                       value='rabbitmq-live.ccptools.cc',
                       description='Give it a meaningful description')

# Create a group shared secret for production
pa.create_shared_secret(name='RABBIT_MQ_PASSWORD',
                        folder='rabbitmq',
                        value='notThatMuchBetterPassword',
                        description='Give it a meaningful description')
```

