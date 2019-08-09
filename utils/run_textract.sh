#!/bin/bash

aws textract detect-document-text --document '{"S3Object":{"Bucket":"philvarner-sources","Name":"daily_progress/2105630.jpg"}}'
