#!/bin/bash

get_tags_from_docker_hub() {
    curl -L -s \
        "https://registry.hub.docker.com/v2/repositories/$1/tags?page_size=1024" |
        jq '."results"[]["name"]' 2> /dev/null |
        tr -d '"'
}

get_version_from_dockerfile() {
    grep "^LABEL" "$1" |
        grep "software.version=" |
        grep -oP '\"([0-9\.]+)\"$' |
        tr -d '"'
}

get_img_name_from_dockerfile() {
    grep "^LABEL" "$1" |
        grep "image.name=" |
        grep -oP '=\".+\"$' |
        tr -d '="'

}

push_docker_if_new_version() {
    new_tag="v$(get_version_from_dockerfile "$1")"
    name="$(get_img_name_from_dockerfile  "$1")"
    img_tag="$name:$new_tag"
    echo "Checking if version changed for $img_tag:"
    # now query the old tags from Docker Hub
    old_tags="$(get_tags_from_docker_hub "$name")"
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

export -f get_tags_from_docker_hub
export -f get_version_from_dockerfile
export -f get_img_name_from_dockerfile
export -f push_docker_if_new_version
# get version
find . -name Dockerfile -exec bash -c 'push_docker_if_new_version $1' shell {} \;
