#!/bin/bash

get-tags-from-docker-hub() {
    wget -q "https://registry.hub.docker.com/v1/repositories/$1/tags" -O -  |
        sed -e 's/[][]//g' -e 's/"//g' -e 's/ //g' | 
        tr '}' '\n'  | 
        awk -F: '{print $3}'
}

get-version-from-dockerfile() {
    grep "^LABEL" "$1" |
        grep "software.version=" |
        grep -oP '\"([0-9\.]+)\"$' |
        tr -d '"'
}

get-img-name-from-dockerfile() {
    grep "^LABEL" "$1" |
        grep "image.name=" |
        grep -oP '=\".+\"$' |
        tr -d '="'

}

push-docker-if-new-version() {
    echo "$1"
    new_tag="v$(get-version-from-dockerfile "$1")"
    echo "$new_tag"
    name="$(get-img-name-from-dockerfile  "$1")"
    old_tags="$(get-tags-from-docker-hub "$name")"
    img_tag="$name:$new_tag"
    echo "Checking if version changed for $img_tag:"
    # exit if the version tag from the Dockerfile is already on Docker Hub
    if [[ "$old_tags" =~ $new_tag ]]; then
        old_tags_str=$(echo "$old_tags" | tr '\n' ',' | sed 's/,$//;s/,/, /g')
        echo "The current tag ($new_tag) is already on Docker Hub ($old_tags_str) --> do nothing"
        return
    else
        echo "Version changed for $img_tag --> build and push"
        docker build -t "$img_tag" "$(dirname "$1")"
        docker push "$img_tag"
    fi
}

export -f get-tags-from-docker-hub
export -f get-version-from-dockerfile
export -f get-img-name-from-dockerfile
export -f push-docker-if-new-version
# get version
find . -name Dockerfile -exec bash -c 'push-docker-if-new-version $1' shell {} \;
