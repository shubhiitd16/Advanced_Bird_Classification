package com.example.sandeshsen.lagbhag_hogya;


import  android.app.ProgressDialog;
import android.content.ContentValues;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;


import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import static com.example.sandeshsen.lagbhag_hogya.GPSTracker.global.FINALBIRDimg;
import static com.example.sandeshsen.lagbhag_hogya.GPSTracker.global.imgpathp;

public class ImageActivity extends AppCompatActivity {

    String imagepath = null;
    String folderPath = null;
    File sourceFile;
    int totalSize = 0;
    String FILE_UPLOAD_URL = "http://10.17.10.77/upload_image.php";
    ImageButton capture_button;
    ImageButton pick_button;
    ImageButton upload_button;
    ImageView ivImage;
    TextView text;
    ProgressDialog progressDialog;
    GPSTracker gps;
    String lat = "0";
    String lon = "0";
    Uri imageUri;
    ContentValues values;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getSupportActionBar().hide();
        setContentView(R.layout.activity_aud);

        gps = new GPSTracker(this);

        capture_button = findViewById(R.id.button_capture);
        pick_button = findViewById(R.id.button_pick_image);
        upload_button = findViewById(R.id.button_upload_image);
        ivImage = (ImageView) findViewById(R.id.ivImage);
        text = (TextView) findViewById(R.id.texti);
        folderPath = Environment.getExternalStorageDirectory() + "/BirdClassifier" + "/Images";
        progressDialog = new ProgressDialog(this);

        final File folder = new File(folderPath);
        if (!folder.exists()) {
            File wallpaperDirectory = new File(folderPath);
            wallpaperDirectory.mkdirs();
        }


        capture_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(imagepath != null) {
                    File file = new File(imagepath);
                    file.delete();
                }

                Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);

                if (intent.resolveActivity(getPackageManager()) != null) {
                    startActivityForResult(intent, 5);
                }
            }
        });
        pick_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(imagepath != null) {
                    File file = new File(imagepath);
                    file.delete();
                }
                Intent intent = new Intent();
                intent.setType("image/*"); // intent.setType("video/*"); to select videos to upload
                intent.setAction(Intent.ACTION_GET_CONTENT);
                startActivityForResult(Intent.createChooser(intent, "Select Image"), 1);
            }
        });
        upload_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (imagepath != null) {
                    new UploadFileToServer().execute();
                } else {
                    Toast.makeText(getApplicationContext(), "Please select a file to upload.", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private Bitmap getRotatedBitmap(Bitmap source, float angle) {
        Matrix matrix = new Matrix();
        matrix.postRotate(angle);
        Bitmap bitmap1 = Bitmap.createBitmap(source, 0, 0, source.getWidth(), source.getHeight(), matrix, true);
        return bitmap1;
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {

        if (requestCode == 1 && resultCode == RESULT_OK) {
            Uri selectedImageUri = data.getData();
            try {
                Bitmap bitmap = MediaStore.Images.Media.getBitmap(this.getContentResolver(), selectedImageUri);
                ivImage.setImageBitmap(bitmap);
                saveImage(bitmap);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        if (requestCode == 5 && resultCode == RESULT_OK) {
            Bundle bundle = data.getExtras();
            Bitmap bitmap = (Bitmap) bundle.get("data");
            ivImage.setImageBitmap(bitmap);
            saveImage(bitmap);
        }
    }

    private void saveImage(Bitmap finalBitmap) {

        String fname = "/IMG" + System.currentTimeMillis() + ".jpg";
        imagepath = folderPath + fname;
        imgpathp = imagepath;
        File file = new File(folderPath, fname);
        if (file.exists()) file.delete();
        try {
            FileOutputStream out = new FileOutputStream(file);
            finalBitmap.compress(Bitmap.CompressFormat.JPEG, 100, out);
            out.flush();
            out.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public String getRealPathFromURI(Uri contentUri) {
        String[] proj = { MediaStore.Images.Media.DATA };
        Cursor cursor = managedQuery(contentUri, proj, null, null, null);
        int column_index = cursor
                .getColumnIndexOrThrow(MediaStore.Images.Media.DATA);
        cursor.moveToFirst();
        return cursor.getString(column_index);
    }

    private class UploadFileToServer extends AsyncTask<String, String, String> {
        @Override
        protected void onPreExecute() {
            sourceFile = new File(imagepath);
            totalSize = (int) sourceFile.length();
            progressDialog.setMessage("Identifying..");
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
            String fileName = lat + ":" + lon + ":" + System.currentTimeMillis() + ".jpg";

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

                    publishProgress("" + (int) ((progress * 100) / totalSize)); // sending progress percent to publishProgress
                }

                // Write closing boundary and close stream
                out.writeBytes(tail);
                out.flush();
                out.close();

                // Get server response
                BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                String line = "";
                StringBuilder builder = new StringBuilder();
                while ((line = reader.readLine()) != null) {
                    builder.append(line);
                }

                return (builder.toString());

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
            FINALBIRDimg = result.toString();
            Intent intent = new Intent(ImageActivity.this, imgpopup.class);
            startActivity(intent);
            super.onPostExecute(result);
        }

    }
    @Override
    public void onBackPressed() {
        Intent intent = new Intent(ImageActivity.this, MainActivity.class);
        startActivity(intent);
        // Do Here what ever you want do on back press;
    }
}


