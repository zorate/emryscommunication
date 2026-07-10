import os
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, Response
from bson.objectid import ObjectId
from app import db, fs
from datetime import datetime

main_bp = Blueprint('main', __name__)

# --- CORE PUBLIC ROUTES ---

@main_bp.route('/')
def index():
    gallery_items  = db.gallery.find().sort('created_at', -1)
    products_items = db.products.find({'visible': {'$ne': False}}).sort('created_at', -1)
    return render_template('index.html', gallery=gallery_items, products=products_items)


@main_bp.route('/book_appointment', methods=['POST'])
def book_appointment():
    try:
        data = request.form
        appointment_doc = {
            "fullname":  data.get('fullname'),
            "phone":     data.get('phone'),
            "appt_date": data.get('appt_date'),
            "service":   data.get('service'),
            "message":   data.get('message', ''),
            "status":    "Pending",
            "created_at": datetime.utcnow()
        }
        db.appointments.insert_one(appointment_doc)
        return jsonify({"success": True, "message": "Appointment booked! We'll contact you to confirm."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error saving appointment: {str(e)}"}), 500


@main_bp.route('/register_apprentice', methods=['POST'])
def register_apprentice():
    try:
        data = request.form
        apprentice_doc = {
            "fullname":        data.get('fullname'),
            "age":             int(data.get('age', 0)),
            "dob":             data.get('dob'),
            "state_of_origin": data.get('state_of_origin'),
            "lga":             data.get('lga'),
            "phone":           data.get('phone', ''),
            "mother_name":     data.get('mother_name'),
            "father_name":     data.get('father_name'),
            "guardian_option": data.get('guardian_option'),
            "guardian_phone":  data.get('guardian_phone', ''),
            "has_experience":  data.get('has_experience') == 'yes',
            "status":          "Pending",
            "created_at":      datetime.utcnow()
        }
        db.apprentices.insert_one(apprentice_doc)
        return jsonify({"success": True, "message": "Application submitted successfully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error saving application: {str(e)}"}), 500


# --- GRIDFS MEDIA STREAMING ---

@main_bp.route('/media/<file_id>')
def serve_media(file_id):
    try:
        grid_out = fs.get(ObjectId(file_id))
        response = Response(grid_out.read(), mimetype=grid_out.content_type)
        response.headers['Content-Disposition'] = f'inline; filename="{grid_out.filename}"'
        return response
    except Exception as e:
        return f"File not found: {str(e)}", 404


# --- ADMIN ROUTES ---

@main_bp.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    configured_password = os.environ.get('ADMIN_PASSWORD', 'admin')

    if request.method == 'POST':
        if request.form.get('password') == configured_password:
            session['is_admin'] = True
            return jsonify({"success": True, "message": "Access authorized."})
        return jsonify({"success": False, "message": "Incorrect password."}), 401

    if session.get('is_admin'):
        applicants   = list(db.apprentices.find().sort('created_at', -1))
        gallery      = list(db.gallery.find().sort('created_at', -1))
        appointments = list(db.appointments.find().sort('created_at', -1))
        products     = list(db.products.find().sort('created_at', -1))
        return render_template('admin.html',
                               applicants=applicants,
                               gallery=gallery,
                               appointments=appointments,
                               products=products)

    return render_template('admin.html',
                           applicants=[], gallery=[],
                           appointments=[], products=[],
                           login_required=True)


@main_bp.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('main.index'))


@main_bp.route('/admin/action/<app_id>/<action>', methods=['POST'])
def update_application(app_id, action):
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "Unauthorized."}), 403
    new_status = "Approved" if action == "approve" else "Rejected"
    db.apprentices.update_one({"_id": ObjectId(app_id)}, {"$set": {"status": new_status}})
    return jsonify({"success": True, "message": f"Status updated to {new_status}."})


@main_bp.route('/admin/upload_media', methods=['POST'])
def upload_media():
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "Unauthorized."}), 403
    file        = request.files.get('media_file')
    description = request.form.get('description', '')
    if not file:
        return jsonify({"success": False, "message": "No file provided."}), 400
    file_id = fs.put(file, filename=file.filename, content_type=file.content_type)
    db.gallery.insert_one({
        "file_id":      str(file_id),
        "content_type": file.content_type,
        "description":  description,
        "created_at":   datetime.utcnow()
    })
    return jsonify({"success": True, "message": "Gallery updated successfully!"})


@main_bp.route('/admin/upload_product', methods=['POST'])
def upload_product():
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "Unauthorized."}), 403
    name        = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    price       = request.form.get('price', 0)
    category    = request.form.get('category', 'accessories')
    badge       = request.form.get('badge', '').strip()
    image_file  = request.files.get('image_file')
    if not name:
        return jsonify({"success": False, "message": "Product name is required."}), 400
    image_id = None
    if image_file and image_file.filename:
        image_id = str(fs.put(image_file, filename=image_file.filename, content_type=image_file.content_type))
    db.products.insert_one({
        "name":        name,
        "description": description,
        "price":       float(price) if price else 0,
        "category":    category,
        "badge":       badge or None,
        "image_id":    image_id,
        "visible":     True,
        "created_at":  datetime.utcnow()
    })
    return jsonify({"success": True, "message": f'Product "{name}" added to shop!'})


@main_bp.route('/admin/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "Unauthorized."}), 403
    db.products.delete_one({"_id": ObjectId(product_id)})
    return jsonify({"success": True, "message": "Product removed."})


@main_bp.route('/admin/delete_media/<media_id>', methods=['POST'])
def delete_media(media_id):
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "Unauthorized."}), 403
    item = db.gallery.find_one({"_id": ObjectId(media_id)})
    if item:
        try:
            fs.delete(ObjectId(item['file_id']))
        except Exception:
            pass
        db.gallery.delete_one({"_id": ObjectId(media_id)})
    return jsonify({"success": True, "message": "Post deleted."})


@main_bp.route('/admin/update_appointment/<appt_id>/<action>', methods=['POST'])
def update_appointment(appt_id, action):
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "Unauthorized."}), 403
    new_status = "Confirmed" if action == "confirm" else "Cancelled"
    db.appointments.update_one({"_id": ObjectId(appt_id)}, {"$set": {"status": new_status}})
    return jsonify({"success": True, "message": f"Appointment {new_status}."})