from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore, storage
from werkzeug.utils import secure_filename 
from gunicorn.app.wsgiapp import WSGIApplication

# Initialize Firebase
cred = credentials.Certificate({
  "type": "service_account",
  "project_id": "blog-ae720",
  "private_key_id": "57438a6efc3e192d6bb0a1b76a40a56c7574ed6f",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDoJNmSl+JeYkmJ\nvxzIxUDj8LWDTPK0pKXMAgEyhgI0EIkOfxlS0VebaePRsoKBoo4mfTOh+XmyCnTU\nUmxsS9RVl5E/4NLX4dO2PmGvyz7aX5nz+iFw0T0lx9vQCPORU8QiE6TRNK+A/c1A\nF7HlkXM3WOrPqUeSP8z7B5w5lBbFSgKynzk56052Dtq4QOG7vpKV1KYchL0m7EDM\nWSN6OboXi+urjxRNXjfPUT3h4xAQu9wwVTIVE4cgM+OGILfUwzvAAZtG02nh4+it\nyOYr72qfSsog2Ml3d6cE9gDbzRnJFvy88XdJCJwIyshrXs0WmV0z+Nus1kOd47o5\nWH1vEiSjAgMBAAECggEAQxc3TC8aLJXyU92IV5vuc5IDG3XXJQ76nbmsl+nz5BEt\nUyO3cWBwFcnmHhodrpKIy6XekL7VhXeRKTXDAQ9vR+dcgp4awWqSMbbYq6ItQZZk\nm4bcOEs4hV078WVM42DWq9SKiy3TVQ/EzHOspcDCECph/m8ZcLKArsIVy+w5In4C\n2nIL/QgdvkzYt/FJ1VKxFKMS2TqQf7xJR9bvF06+owf2PwUn5qqOEFNCO8euufvU\nqVU76nOllJ7IQJd6PwHhXg6eti2kxY5DcWaV4zApq/pHkvJCnvpzG3BI85cMC6sj\n/dMTuqdNlM6/+mLCvcpCEBzJnDrLu6YD8M33mxK97QKBgQD3G79Gc2o/u4g8EpQh\na6C7JGMhiZU8B/sY0jzujRNUcrxUXKhx7oniWJuo+NgAH47/UVnHKAlMLPYhcVM4\n/cO9ULePsPQzXxSShF63mDq1/3n/oW79VJarex/MXghnHP7a+VIiqR7MLKUcMkRn\nSL+PjjCRcdf1kfwjSPjVb57QRQKBgQDwf0HFd/tAh4yL1fJ4RyKE+IN7GFwrhtQ3\n2Y+L6z1cizXSiR2eUyU7Fr3Dy/3e3PtG/xxvFhuGCOVPotpWfqfZ250M2hbU/YH9\nwFdGobwdPjlQ/hL0xNcZ6RC0LcDrGv2ZCWJklX3263MWrhnqh9g5UxtiJZQacyud\nTrQBDeazxwKBgQDixDXeAyBn6EL3Td1eZhSUaKoIJugqtPA7MQP1rsUkZD5r9LQo\nCc3DR6lhgStHwa5Ko28OErGllEUzH3pN/KLaYu5xEOSpGAIbCxqYxTxrtE1Sx+TA\n2hWCvHTL6Scw6Sz/6njzkdvPZtEGdSLM3bfdl5D+iEi09Qk7oEWqKMrHOQKBgQCF\nO8rhLfYYqr93HKDGd4otJkwY3sb5KinZgwLeXgVRhqHbsDCjbKaclJ2uog1T8RKY\nI27KL/IxkC4Rr0PMVUCCFgNsgknR11uzi2IOdD116enw78Dqrz4HUbH6T7qnxP0n\nUiabWKI/L/NDZlJfNsDYCS2LcwwYlyNbc6WPS/c6MwKBgHMtOOsTfuaMXgY+b3L6\nJdSe2z+dO5Ws8P+pdTAXwcnMlJL0XVf/dZI2YR1XI3Ec1pC5yaEFl3arbOEOfrjm\nKgz/kzWi6Cq1VP5+FfY36HUs7BVR2ou2H3IkzjS/FuJ/qAhNKS2N7UVYQypr7BxK\nl7QI85QhksVA07tuDBSwUW1y\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-bv4ss@blog-ae720.iam.gserviceaccount.com",
  "client_id": "101574573845279959095",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-bv4ss%40blog-ae720.iam.gserviceaccount.com"
})
firebase_admin.initialize_app(cred, {
    'storageBucket': 'blog-ae720.appspot.com'
})
db = firestore.client()
bucket = storage.bucket()

app = Flask(__name__)
app.secret_key = 'f9bf78b9a18ce6d46a0cd2b0b86df9da'  

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files['image']
        video = request.files['video']
        timestamp = datetime.utcnow()

        image_url = None
        video_url = None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            blob = bucket.blob(f'uploads/{filename}')
            blob.upload_from_string(image.read(), content_type=image.content_type)
            blob.make_public()
            image_url = f'https://storage.googleapis.com/{bucket.name}/{blob.name}'

        if video and allowed_file(video.filename):
            filename = secure_filename(video.filename)
            blob = bucket.blob(f'uploads/{filename}')
            blob.upload_from_string(video.read(), content_type=video.content_type)
            blob.make_public()
            video_url = f'https://storage.googleapis.com/{bucket.name}/{blob.name}'

        post_data = {
            'title': title,
            'content': content,
            'image_url': image_url,
            'video_url': video_url,
            'timestamp': timestamp
        }
        db.collection('posts').add(post_data)
        flash("Post added successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    posts_ref = db.collection('posts').order_by('timestamp', direction=firestore.Query.DESCENDING)
    posts = [{'id': doc.id, **doc.to_dict()} for doc in posts_ref.stream()]
    return render_template('admin_dashboard.html', posts=posts)

@app.route('/delete_post/<post_id>', methods=['POST'])
def delete_post(post_id):
    db.collection('posts').document(post_id).delete()
    flash("Post deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/blog')
def blog():
    posts_ref = db.collection('posts').order_by('timestamp', direction=firestore.Query.DESCENDING)
    posts = [doc.to_dict() for doc in posts_ref.stream()]
    return render_template('blog.html', posts=posts)

@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post_ref = db.collection('posts').document(post_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files['image']
        video = request.files['video']

        # Get the existing post data 
        post_data = post_ref.get().to_dict()

        # Update the post data with the form data
        post_data['title'] = title
        post_data['content'] = content

        # Update the image 
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            blob = bucket.blob(f'uploads/{filename}')
            blob.upload_from_string(image.read(), content_type=image.content_type)
            blob.make_public()
            post_data['image_url'] = f'https://storage.googleapis.com/{bucket.name}/{blob.name}'

        # Update the video 
        if video and allowed_file(video.filename):
            filename = secure_filename(video.filename)
            blob = bucket.blob(f'uploads/{filename}')
            blob.upload_from_string(video.read(), content_type=video.content_type)
            blob.make_public()
            post_data['video_url'] = f'https://storage.googleapis.com/{bucket.name}/{blob.name}'

        # Update the post in Firestore
        post_ref.set(post_data)

        flash("Post updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    # Get the existing post data from Firestore and pass it to the template
    post_data = post_ref.get().to_dict()
    return render_template('edit_post.html', post=post_data)

if __name__ == '__main__':
    options = {
        'bind': '0.0.0.0:8000',
        'workers': 4
    }
    WSGIApplication(app).run()