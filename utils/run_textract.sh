#!/bin/bash

aws textract detect-document-text --document '{"S3Object":{"Bucket":"philvarner-sources","Name":"daily_progress/2105630.jpg"}}'

aws textract start-document-text-detection --document-location '{"S3Object":{"Bucket":"cville-documents","Name":"campaignfromwild00vena.pdf"}}'

aws textract get-document-text-detection --job-id 4a140ca0ac16efb067ec8fe96ae840ff7bfe97583817c3e4aa04d500a3c9c925