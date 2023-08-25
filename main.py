import requests
from flask import Flask, request, jsonify
from instagrapi import Client

client = Client()

app = Flask(__name__)

@app.route("/")
def home():
    return "Home"

@app.route("/get")
async def get_user():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL parameter is missing"}), 400
    try:
        # Asynchronously fetch media information
        media = client.media_info(client.media_pk_from_url(url)).dict()

        resources = media.get("resources", [])

        single_video = media.get("video_url")

        media_urls = []

        if single_video:
            media_urls.append(get_proxy_url(single_video))

        for resource in resources:
            video_url = resource.get("video_url")
            thumbnail_url = resource.get("thumbnail_url")
            if video_url:
                proxy_url = get_proxy_url(video_url)
                media_urls.append(proxy_url)
            elif thumbnail_url:     
                proxy_url = get_proxy_url(thumbnail_url)
                media_urls.append(proxy_url)

        response = {
            "url_list": media_urls,
            "isError": False
        }

        return jsonify(response)
    except Exception as e:
        error_response = {
            "url_list": [],
            "isError": True,
            "message": e,
        }
        return jsonify(error_response)


@app.route("/proxy")
def proxy():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL parameter is missing"}), 400

    try:
        response = requests.get(url, stream=True)
        headers = dict(response.headers)
        headers.pop("Content-Encoding", None)
        headers.pop("Transfer-Encoding", None)
        return response.content, response.status_code, headers
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-user-post")
def get_post_by_username():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username parameter is missing"}), 400

    try:
        # Get user if from username 
        userId =  client.user_id_from_username(username=username)

        # Get user media from userId 
        medias = client.user_medias(user_id=userId, amount=100)

        media_urls = []
        for media in medias:
            # media_list.append(media.dict())
            media_dict = media.dict()
            if media_dict.get("video_url") :
                media_urls.append(get_proxy_url(media_dict.get("video_url")))
                # print(media_dict.get("media_type"))
            elif media_dict.get("thumbnail_url") :
                media_urls.append(get_proxy_url(media_dict.get("thumbnail_url")))
                # print(media_dict.get("media_type"))
            else:
                resources = media_dict.get("resources", [])
                for resource in resources:
                    video_url = resource.get("video_url")
                    thumbnail_url = resource.get("thumbnail_url")
                    if video_url:
                        proxy_url = get_proxy_url(video_url)
                        media_urls.append(proxy_url)
                    elif thumbnail_url:     
                        proxy_url = get_proxy_url(thumbnail_url)
                        media_urls.append(proxy_url)
        return jsonify(media_urls)

    except Exception as e:
        error_response = {
            "url_list": [],
            "isError": True,
            "message": e,
        }
        return jsonify(error_response)
def get_proxy_url(url):
    return f"http://localhost:5000/proxy?url={requests.utils.quote(url)}"



if __name__ == "__main__":
    app.run(debug=True)
