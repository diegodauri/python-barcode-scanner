from __future__ import print_function
import cloudmersive_barcode_api_client
from cloudmersive_barcode_api_client.rest import ApiException
from flask import Flask, request, render_template, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "./static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config["SECRET_KEY"] = "123456789"

# Configure API key authorization: Apikey
configuration = cloudmersive_barcode_api_client.Configuration()
configuration.api_key['Apikey'] = '2f177b90-fff6-4821-9142-8c7314c285fe'


def scan_barcode(img):
    # create an instance of the API class
    api_instance = cloudmersive_barcode_api_client.BarcodeScanApi(
        cloudmersive_barcode_api_client.ApiClient(configuration))
    image_file = img  # file | Image file to perform the operation on.  Common file formats such as PNG, JPEG are supported.

    try:
        # Scan and recognize an image of a barcode
        api_response = api_instance.barcode_scan_image(image_file)
        if api_response.successful:
            return api_response.raw_text
        else:
            return False
    except ApiException as e:
        print("Exception when calling BarcodeScanApi->barcode_scan_image: %s\n" % e)


def create_barcode(text):
    api_instance = cloudmersive_barcode_api_client.GenerateBarcodeApi(
        cloudmersive_barcode_api_client.ApiClient(configuration))
    value = text  # str | UPC-A barcode value to generate from

    try:
        # Generate a UPC-A code barcode as PNG file
        api_response = api_instance.generate_barcode_upca(value)
        return api_response
    except ApiException as e:
        print("Exception when calling GenerateBarcodeApi->generate_barcode_upca: %s\n" % e)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return redirect(url_for("scan", filename=filename))
    return render_template("upload.html")

@app.route("/scan/<filename>")
def scan(filename):
    img = os.path.join(UPLOAD_FOLDER, filename)
    response = scan_barcode(img)
    if response:
        return render_template("scan.html", barcode=response)
    else:
        return "Error"

@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        text = request.form["value"]
        response = create_barcode(text)
        if response:
            return response
        else:
            flash("Not an UPC-A sting!")
    return render_template("create.html")

if __name__ == "__main__":
    app.run(debug=True)
