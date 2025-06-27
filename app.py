from flask import Flask, render_template, request, send_file, jsonify
from moviepy.editor import VideoFileClip
from tempfile import NamedTemporaryFile

app = Flask(__name__)
app.secret_key = "supersecretkey"

print("✅ moviepy imported successfully")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/trim', methods=['POST'])
def trim():
    try:
        if 'video' not in request.files:
            return jsonify({"error": "No video file uploaded."}), 400

        video_file = request.files['video']
        start_str = request.form.get('start', '0')
        end_str = request.form.get('end', '0')

        try:
            start = float(start_str)
            end = float(end_str)
        except ValueError:
            return jsonify({"error": "Start and end times must be numbers."}), 400

        with NamedTemporaryFile(delete=False, suffix='.mp4') as temp_in:
            video_file.save(temp_in.name)

            clip = VideoFileClip(temp_in.name)
            duration = clip.duration

            # clamp
            start = max(0, min(start, duration))
            end = max(start, min(end, duration))

            if start >= end:
                clip.close()
                return jsonify({"error": "End time must be greater than start time."}), 400

            trimmed = clip.subclip(start, end)

            with NamedTemporaryFile(delete=False, suffix='.mp4') as temp_out:
                trimmed.write_videofile(temp_out.name, codec="libx264", audio_codec="aac")

                clip.close()
                trimmed.close()

                # return file as attachment
                return send_file(temp_out.name, mimetype="video/mp4")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)



