from flask import Flask, request, jsonify, send_file, abort

def create_api(name, application_layer=None):
    server = Flask(name)
    
    @server.route('/dl/segmentation', methods=['PUT'])
    def segment_plant():
        if request.mimetype != 'multipart/form-data':
            print(f"{request.content_type} is not 'multipart/form-data'")
            abort(400)
        elif 'image' not in request.files:
            abort(400)
        else:
            return jsonify({"plant_id": application_layer.segment_plant(request.files['image'].read())})
    
    @server.route('/perf/segmentation', methods=['PUT'])
    def perf_test_segementation():
        if request.mimetype != 'multipart/form-data':
            print(f"{request.content_type} is not 'multipart/form-data'")
            abort(400)
        elif 'image' not in request.files:
            abort(400)
        else:
            plant_id = application_layer.segment_plant(request.files['image'].read())
            (image_data, mimetype) = application_layer.get_image(plant_id, 'segmentation')
            return send_file(image_data, mimetype=mimetype)
        
    @server.route('/plant/status', methods=['GET'])
    def get_plant_status():
        plant_id = request.args.get('plant_id')
        return jsonify({"status": application_layer.plant_status(plant_id)})
    
    @server.route('/plant/data', methods=['GET'])
    def get_plant_data():
        plant_id = request.args.get('plant_id')
        return jsonify(application_layer.plant_data(plant_id))
    
    @server.route('/plant/image', methods=['GET'])
    def get_plant_item():
        plant_id = request.args.get('plant_id')
        image_name = request.args.get('image_name')
        (image_data, mimetype) = application_layer.get_image(plant_id, image_name)
        if image_data:
            return send_file(image_data, mimetype=mimetype)
        else: 
            abort(400)

    @server.route('/plant/ids', methods=['GET'])
    def get_plant_ids():
        return jsonify({"plant_ids": application_layer.get_plant_ids()})

    return server
