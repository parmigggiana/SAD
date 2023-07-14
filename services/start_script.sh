#!/bin/sh

# Function to recursively search for files in directories
search_directories() {
    local visited_dir="$1"

    # Iterate over all directories in the current directory
    for dir in */; do
        # Check if the directory has already been visited
        if [ "$visited_dir" != "" ] && [ "$visited_dir/$dir" -ef "$dir" ]; then
            continue
        fi

        # Move into the directory
        cd "$dir" || continue
        echo "Checking directory: $dir"

        # Search for the files in the specified order
        if [ -f "deploy.sh" ]; then
            echo "Found deploy.sh in $dir"
            chmod +x "$(pwd)/deploy.sh"
            /bin/sh -c "$(pwd)/deploy.sh"

        elif [ -f "docker-compose.yml" ]; then
            echo "Found docker-compose.yml in $dir"
            docker compose up -d --build

        elif [ -f "docker-compose.yaml" ]; then
            echo "Found docker-compose.yaml in $dir"
            docker compose up -d --build

        elif [ -f "Dockerfile" ]; then
            echo "Found Dockerfile in $dir"
            docker build --tag '$dir' .
            docker run -d '$dir'

        else
            # No matching file found, recursively search subdirectories
            search_directories "$PWD"
        fi

        # Move back to the parent directory
        cd ..
    done
}

# Start searching from the current working directory
cd /root
search_directories
