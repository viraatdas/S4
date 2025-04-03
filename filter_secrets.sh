#!/bin/bash

# This script is used with git filter-branch to remove sensitive information from the repository history

# Function to filter files and replace sensitive information
filter_file() {
    # Replace Google OAuth credentials
    sed -i '' 's/952024236906-skd03vg8rbrlg8gbcb7h8nafqhgpmk6a\.apps\.googleusercontent\.com/YOUR_GOOGLE_CLIENT_ID/g' "$@"
    sed -i '' 's/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/YOUR_GOOGLE_CLIENT_SECRET/g' "$@"
    
    # Replace SuperTokens credentials
    sed -i '' 's/st-dev-7fccbc80-101f-11f0-8dcf-2382362cfcad\.aws\.supertokens\.io/YOUR_SUPERTOKENS_URI/g' "$@"
    sed -i '' 's/q2sB3jUZAL2Ceju85rWQNyZerJ/YOUR_SUPERTOKENS_API_KEY/g' "$@"
    
    # Replace OpenAI API Key (pattern matching for potential API keys)
    sed -i '' 's/sk-[a-zA-Z0-9]\{48\}/YOUR_OPENAI_API_KEY/g' "$@"
    sed -i '' 's/sk-proj-[a-zA-Z0-9]\{150,\}/YOUR_OPENAI_API_KEY/g' "$@"
}

# Check if a file exists and filter it
if [ -f "$1" ]; then
    # Apply filtering based on file extension or filename
    case "$1" in
        *.js|*.py|*.sh|*.config|*.example|*.html|*.json|*task-def*.json)
            filter_file "$1"
            ;;
    esac
fi
