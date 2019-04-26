package com.example.sandeshsen.lagbhag_hogya;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.media.MediaPlayer;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Environment;
import android.os.Handler;
import android.provider.MediaStore;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import org.w3c.dom.Text;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import static java.lang.Thread.sleep;

public class AudioActivity extends AppCompatActivity {

    String audiopath = null;
    String folderPath = null;
    File sourceFile;
    int totalSize = 0;
    String FILE_UPLOAD_URL = "http://10.17.10.77/upload_audio.php";
    ImageButton record_button;
    ImageButton pick_button;
    ImageButton upload_button;
    ImageButton play_button;
    TextView sel;
    MediaRecorder mediaRecorder;
    TextView text;
    ProgressDialog progressDialog;
    String lat = "0";
    String lon = "0";
    GPSTracker gps;
    int records = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getSupportActionBar().hide();
        setContentView(R.layout.activity_img);
        sel = findViewById(R.id.selected);

        gps = new GPSTracker(this);

        record_button = findViewById(R.id.button_record);
        pick_button = findViewById(R.id.button_pick_audio);
        play_button = findViewById(R.id.button_play_audio);
        upload_button = findViewById(R.id.button_upload_audio);
        text = findViewById(R.id.texti);
        progressDialog = new ProgressDialog(this);

        folderPath = Environment.getExternalStorageDirectory() + "/BirdClassifier" + "/Audios";

        final File folder = new File(folderPath);
        if (!folder.exists()) {
            File wallpaperDirectory = new File(folderPath);
            wallpaperDirectory.mkdirs();
        }


        record_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(audiopath != null && records == 1){
                    File file = new File(audiopath);
                    file.delete();
                }
                records = 1;
                record();
                sel.setText("Audio Selected");
            }
        });
        pick_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                records = 0;
                Intent intent = new Intent();
                intent.setType("audio/*"); // intent.setType("video/*"); to select videos to upload
                intent.setAction(Intent.ACTION_GET_CONTENT);
                startActivityForResult(Intent.createChooser(intent, "Select Audio"), 1);
            }
        });
        play_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (audiopath != null) {
                    play_audio();
                }else{
                    Toast.makeText(getApplicationContext(), "Please select a file to play.", Toast.LENGTH_SHORT).show();
                }
            }
        });
        upload_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (audiopath != null) {
                    new UploadFileToServer().execute();
                }else{
                    Toast.makeText(getApplicationContext(), "Please select a file to upload.", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == 1 && resultCode == Activity.RESULT_OK) {
            if ((data != null) && (data.getData() != null)) {
                Uri audioFileUri = data.getData();
                String XXXX = audioFileUri.getPath();
                String[] tt = XXXX.split(":");
                audiopath = Environment.getExternalStorageDirectory() + "/" + tt[1];
                    sel.setText("Audio Selected");
                // Now you can use that Uri to get the file path, or upload it, ...
            }
        }
    }

    private void record(){
        record_button.setEnabled(false);
        pick_button.setEnabled(false);
        upload_button.setEnabled(false);

        progressDialog.setMessage("Recording");
        progressDialog.setCancelable(false);
        progressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
        progressDialog.show();
        audiopath = folderPath + "/AUD" + System.currentTimeMillis() + ".mp3";
        MediaRecorderReady();
        try {
            mediaRecorder.prepare();
            mediaRecorder.start();
        } catch (IllegalStateException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            public void run() {
                // Actions to do after 10 seconds
                mediaRecorder.stop();
                mediaRecorder.release();
                mediaRecorder = null;
                progressDialog.dismiss();
            }
        }, 5000);
        /*try {
            sleep(5000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }*/




        record_button.setEnabled(true);
        pick_button.setEnabled(true);
        upload_button.setEnabled(true);
    }

    public void play_audio(){
        String path = audiopath;
        MediaPlayer player = new MediaPlayer();

        try {
            player.setDataSource(path);
            player.prepare();
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        } catch (Exception e) {
            System.out.println("Exception of type : " + e.toString());
            e.printStackTrace();
        }

        player.start();
    }

    public void MediaRecorderReady() {
        mediaRecorder = new MediaRecorder();
        mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP);
        mediaRecorder.setAudioEncoder(MediaRecorder.OutputFormat.AMR_NB);
        mediaRecorder.setAudioEncodingBitRate(1600000);
        mediaRecorder.setAudioSamplingRate(44100);
        mediaRecorder.setOutputFile(audiopath);
    }

    private class UploadFileToServer extends AsyncTask<String, String, String> {
        @Override
        protected void onPreExecute() {
            sourceFile = new File(audiopath);
            totalSize = (int)sourceFile.length();
            progressDialog.setMessage("Identifing..");
            progressDialog.setCancelable(false);
            progressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
            progressDialog.show();
            super.onPreExecute();
        }

        @Override
        protected void onProgressUpdate(String... progress) {
            Log.d("PROG", progress[0]);
        }

        @Override
        protected String doInBackground(String... args) {
            HttpURLConnection.setFollowRedirects(false);
            HttpURLConnection connection = null;
            lat = Double.toString(gps.getLatitude());
            lon = Double.toString(gps.getLongitude());
            String fileName = lat + ":" + lon + ":" + System.currentTimeMillis() + ".mp3";

            try {
                connection = (HttpURLConnection) new URL(FILE_UPLOAD_URL).openConnection();
                connection.setRequestMethod("POST");
                String boundary = "---------------------------boundary";
                String tail = "\r\n--" + boundary + "--\r\n";
                connection.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + boundary);
                connection.setDoOutput(true);

                String metadataPart = "--" + boundary + "\r\n"
                        + "Content-Disposition: form-data; name=\"metadata\"\r\n\r\n"
                        + "" + "\r\n";

                String fileHeader1 = "--" + boundary + "\r\n"
                        + "Content-Disposition: form-data; name=\"fileToUpload\"; filename=\""
                        + fileName + "\"\r\n"
                        + "Content-Type: application/octet-stream\r\n"
                        + "Content-Transfer-Encoding: binary\r\n";

                long fileLength = sourceFile.length() + tail.length();
                String fileHeader2 = "Content-length: " + fileLength + "\r\n";
                String fileHeader = fileHeader1 + fileHeader2 + "\r\n";
                String stringData = metadataPart + fileHeader;

                long requestLength = stringData.length() + fileLength;
                connection.setRequestProperty("Content-length", "" + requestLength);
                connection.setFixedLengthStreamingMode((int) requestLength);
                connection.connect();

                DataOutputStream out = new DataOutputStream(connection.getOutputStream());
                out.writeBytes(stringData);
                out.flush();

                int progress = 0;
                int bytesRead = 0;
                byte buf[] = new byte[1024];
                BufferedInputStream bufInput = new BufferedInputStream(new FileInputStream(sourceFile));
                while ((bytesRead = bufInput.read(buf)) != -1) {
                    // write output
                    out.write(buf, 0, bytesRead);
                    out.flush();
                    progress += bytesRead; // Here progress is total uploaded bytes

                    publishProgress(""+(int)((progress*100)/totalSize)); // sending progress percent to publishProgress
                }

                // Write closing boundary and close stream
                out.writeBytes(tail);
                out.flush();
                out.close();

                // Get server response
                BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                String line = "";
                StringBuilder builder = new StringBuilder();
                while((line = reader.readLine()) != null) {
                    builder.append(line);
                }

                return builder.toString();

            } catch (Exception e) {
                // Exception
            } finally {
                if (connection != null) connection.disconnect();
            }
            return null;
        }

        @Override
        protected void onPostExecute(String result) {
            Log.e("Response", "Response from server: " + result);
            progressDialog.dismiss();
            text.setText(result.toString());
            GPSTracker.global.FINALBIRD = result.toString();
            Intent intent = new Intent(AudioActivity.this, popup.class);
            startActivity(intent);
            super.onPostExecute(result);
        }

    }
    @Override
    public void onBackPressed() {
        Intent intent = new Intent(AudioActivity.this, MainActivity.class);
        startActivity(intent);
        // Do Here what ever you want do on back press;
    }
}


