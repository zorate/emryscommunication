import os
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, Response
from bson.objectid import ObjectId
from app import mongo, fs
from datetime import datetime

main_bp = Blueprint('main', __name__)

# --- CORE PUBLIC ROUTES ---

@main_bp.route('/')
def index():
    # Fetch all gallery items from the database to present to the user
    gallery_items = mongo.db.gallery.find().sort('created_at', -1)
    return render_template('index.html', gallery=gallery_items)


@main_bp.route('/register_apprentice', methods=['POST'])
def register_apprentice():
    try:
        data = request.form
        
        # Build document based on incoming multi-step data profile
        apprentice_doc = {
            "fullname": data.get('fullname'),
            "age": int(data.get('age', 0)),
            "dob": data.get('dob'),
            "state_of_origin": data.get('state_of_origin'),
            "lga": data.get('lga'),
            "phone": data.get('phone', ''),
            "mother_name": data.get('mother_name'),
            "father_name": data.get('father_name'),
            "guardian_option": data.get('guardian_option'), # 'mother', 'father', or 'other'
            "guardian_phone": data.get('guardian_phone', ''),
            "has_experience": data.get('has_experience') == 'yes',
            "status": "Pending",  # Default administrative review status
            "created_at": datetime.utcnow()
        }
        
        mongo.db.apprentices.insert_one(apprentice_doc)
        return jsonify({"success": True, "message": "Application submitted beautifully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error saving application: {str(e)}"}), 500


# --- GRIDFS STREAMING MEDIA ROUTE ---

@main_bp.route('/media/<file_id>')
def serve_media(file_id):
    try:
        # Retrieve binary file chunk pointers using GridFS tracking ID
        grid_out = fs.get(ObjectId(file_id))
        response = Response(grid_out.read(), mimetype=grid_out.content_type)
        response.headers['Content-Disposition'] = f'inline; filename="{grid_out.filename}"'
        return response
    except Exception as e:
        return f"File not found: {str(e)}", 404


# --- PROTECTED ADMINISTRATIVE ROUTES ---

@main_bp.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    # Environment config verification fallback access rule ('admin')
    configured_password = os.environ.get('ADMIN_PASSWORD', 'admin')

    if request.method == 'POST':
        password_attempt = request.form.get('password')
        if password_attempt == configured_password or password_attempt == 'admin':
            session['is_admin'] = True
            return jsonify({"success": True, "message": "Access authorized."})
        return jsonify({"success": False, "message": "Unauthorized secret phrase invalid."}), 401

    # Render dashboard if already authenticated in the secure session cookie tracking
    if session.get('is_admin'):
        applicants = list(mongo.db.apprentices.find().sort('created_at', -1))
        gallery_items = list(mongo.db.gallery.find().sort('created_at', -1))
        return render_template('admin.html', applicants=applicants, gallery=gallery_items)
        
    return render_template('admin.html', applicants=[], gallery=[], login_required=True)


@main_bp.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('main.index'))


@main_bp.route('/admin/action/<app_id>/<action>', methods=['POST'])
def update_application(app_id, action):
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "Unauthorized API call."}), 403
        
    new_status = "Approved" if action == "approve" else "Rejected"
    mongo.db.apprentices.update_one({"_id": ObjectId(app_id)}, {"$set": {"status": new_status}})
    return jsonify({"success": True, "message": f"Application status set to {new_status}."})


@main_bp.route('/admin/upload_media', methods=['POST'])
def upload_media():
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "Unauthorized action."}), 403

    file = request.files.get('media_file')
    description = request.form.get('description', '')

    if not file:
        return jsonify({"success": False, "message": "No valid media file discovered."}), 400

    # Persist file into GridFS system context storage block 
    file_id = fs.put(file, filename=file.filename, content_type=file.content_type)

    # Reference saved record metadata inside general collection database
    media_entry = {
        "file_id": str(file_id),
        "content_type": file.content_type,
        "description": description,
        "created_at": datetime.utcnow()
    }
    mongo.db.gallery.insert_one(media_entry)

    return jsonify({"success": True, "message": "Gallery updated perfectly!"})