#!/bin/bash

if [ "$1" == "deploy" ]; then
    # Build the environment variable string
    ENV_VARS=$(grep -v '^#' .env | xargs | tr ' ' ',')

    # Google Cloud Run deployment
    gcloud run deploy lifex-backend-api-users-v1 --source . \
        --update-env-vars "$ENV_VARS" \
        --allow-unauthenticated \
        --vpc-connector alloydb-connector \
        --platform managed \
        --region europe-west2

elif [ "$1" == "vocodeDemo" ]; then

    # Google Cloud Run deployment
    gcloud run deploy lifex-vocode-demo-v1 --source ./vocode-sdk-demo/ \
        --update-env-vars "$ENV_VARS" \
        --allow-unauthenticated \
        --vpc-connector alloydb-connector \
        --platform managed \
        --region europe-west2

else
    echo "Usage: ./deploy_script.sh deploy"
fi