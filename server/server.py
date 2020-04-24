from flask import Flask, request, send_file
from flask_cors import CORS
import requests

from matplotlib import pyplot as plt
from PIL import Image
import numpy as np
import utils
import json
import base64
from io import BytesIO
import random
import string

from fake_useragent import UserAgent


app = Flask(__name__)

CORS(app, support_credentials=True)

DEEPLAB = utils.init_deeplab()
PIX2PIX = utils.init_pix2pix()
API_TOKEN = 'YOUR-API-TOKEN';

@app.route('/getpano', methods=['GET'])
def getpano():

	x = request.args.get('x')
	y = request.args.get('y')

	url = 'https://maps.googleapis.com/maps/api/streetview/metadata?location='+ x + '%2C' + y + '&key=' + API_TOKEN

	req = requests.get(url).content
	pano_id = json.loads(req)['pano_id']

	print('Got pano id: ', pano_id)

	if len(pano_id) > 22:
		return "Sorry. This panorama cannot be downloaded due to Google Map restrictions.", 400

	pano = Image.new('RGB', (13312, 6656)) # creates a new empty image

	for i in range(26):
		for j in range(13):
			uri = 'http://cbk0.google.com/cbk?output=tile&panoid=' + pano_id + '&zoom=5&x=' + str(i) + '&y=' + str(j)
			
			ua = UserAgent()
			headers = {'User-Agent': 'ua.random'}

			req = requests.get(uri, headers=headers)
			img =  base64.b64encode(req.content).decode("utf-8")
			inp = Image.open(BytesIO(base64.b64decode(img)))

			pano.paste(inp, (i * 512, j * 512))

	print('Got full panorama...')

	# Temporary way to process panorama images
	width, height = pano.size
	print('PANO SIZE: =============================', width, height)
	if height >= 10000 or width >= 10000:
		pano = utils.compress_image(pano, 8)

	pano.save('./images/pano/' + pano_id + '.jpg')

	return send_file('./images/pano/' + pano_id + '.jpg', mimetype='image/jpg', as_attachment=True)



@app.route('/remove', methods=['POST'])
def remove():

	image = request.files.get('filedata', '')
	filename = ''

	if image.filename == 'blob':
		filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
	elif image.filename.split('.')[1] == 'jpg' or image.filename.split('.')[1] == 'jpeg':
		filename = image.filename.split('.')[0]
	else:
		return "Please, upload .JPEG image.", 400

	inp = Image.open(image)

	print('Got input image...')

	inp.save('./images/' + filename + '-0.jpg')

	# Temporary way to process panorama images
	width, height = inp.size
	if height >= 10000 or width >= 10000:
		inp = utils.compress_image(inp, 8)

	seg, bboxes = utils.segmentate_objects(DEEPLAB, inp)

	print('Segmentated image...')

	#plt.imsave('./images/' + filename + '-1.jpg', inp  * 0.5 + 0.5)

	res = utils.remove_objects(PIX2PIX, np.array(inp), seg, bboxes)

	print('Removed objects...')

	plt.imsave('./images/' + filename + '-2.jpg', res * 0.5 + 0.5)

	return send_file('./images/' + filename + '-2.jpg', mimetype='image/jpg', as_attachment=True)



if __name__ == '__main__':

	app.run()