# ICTS Dashboard
A proof-of-concept for a genomic metadata DB with API access. This database is designed to be deployed in a variaty of environments. If configurd properly it should work with any external application that presents properly formatted API requests with appropirate aauthentication credentials. 

This repository is composed of two serivce applications. The `server` application is a Django API DB and the `client` application is a Redux/React UI.

For general usage see our [User Guide](docs/user_guide.md)
## Deployment

- [Local deployment](docs/deployment/localDeployment.md) 
    - For develpment or internal use only
- [Production deployment](docs/deployment/productionDeployment.md)
    - For deployment that is exposed to the internet
- [Docker deployment](docs/deployment/dockerDeployment.md)
    - WIP: comming soon

## Development and troubleshooting
- [Contribution Guide lines](docs/CONTRIBUTING.md)
- [FAQ and trouble shooting](docs/faq.md)
- [`.secretes` configuration](docs/config.md)
- [Testing](docs/testing.md)
