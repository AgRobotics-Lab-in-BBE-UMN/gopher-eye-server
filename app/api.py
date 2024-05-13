from flask import Flask, request, jsonify, send_file, abort

def create_api(name, application_layer=None):
    server = Flask(name)
    
    @server.route('/dl/segmentation', methods=['PUT'])
    def submit_segmentation_job():
        if request.mimetype != 'multipart/form-data':
            abort(400)
        elif 'image' not in request.files:
            abort(400)
        else:
            return jsonify({"job_id": application_layer.submit_job(request.files['image'].read())})
        
    @server.route('/job/status', methods=['GET'])
    def get_job_status():
        job_id = request.json['job_id']
        return jsonify({"status": application_layer.job_status(job_id)})
    
    @server.route('/job/data', methods=['GET'])
    def get_job_data():
        job_id = request.json['job_id']
        return jsonify(application_layer.job_data(job_id))
    
    @server.route('/job/image', methods=['GET'])
    def get_job_item():
        job_id = request.json['job_id']
        image_name = request.json['image']
        image_data = application_layer.get_image(job_id, image_name)
        if image_data:
            return send_file(image_data, mimetype='image/jpeg')
        else: 
            abort(400)

    return server

if __name__ == '__main__':
    app = create_api(__name__)
    app.run(host="10.0.1.20", port=5000)
