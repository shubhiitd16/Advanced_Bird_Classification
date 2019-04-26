package com.example.sandeshsen.lagbhag_hogya;


import android.app.AlertDialog;
import android.app.Service;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.hardware.Camera;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.media.MediaRecorder;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.os.IBinder;
import android.provider.Settings;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import static java.lang.Thread.sleep;


public class CollectorActivity extends AppCompatActivity {

    //For Location
    protected LocationManager locationManager;
    protected LocationListener locationListener;
    protected Context context;
    int totalSize = 0;
    TextView txtLat;
    String lat;
    String lon;
    protected String latitude, longitude;
    protected boolean gps_enabled, network_enabled;
    //
    File sourceFile;
    String zipfile = "";
    private FrameLayout frameCamera;
    private Camera camera;
    private CameraPreview cameraPreview;
    private Button btnCapImg;
    private Button btnRCamera;
    private int cameraType = 0;
    String FILE_UPLOAD_URL = "http://10.17.10.77/collection.php";

    String folderPath = null;
    String uploadfolder = null;
    MediaRecorder mediaRecorder;
    String AudioSavePathInDevice = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_collector);

        final Spinner Mine = (Spinner) findViewById(R.id.spinner);
        ArrayAdapter<String> Me = new ArrayAdapter<String>(CollectorActivity.this,
                android.R.layout.simple_list_item_1, getResources().getStringArray(R.array.Bird));
        Me.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        Mine.setAdapter(Me);


        txtLat = (TextView) findViewById(R.id.textview1);
        GPSTracker gps = new GPSTracker(this);
        double latitude = gps.getLatitude();
        double longitude = gps.getLongitude();
        lat = Double.toString(latitude);
        lon = Double.toString(longitude);
        txtLat.setText("Help Us By telling about your bird" );


        frameCamera = (FrameLayout) findViewById(R.id.frameCamera);
        btnCapImg = (Button) findViewById(R.id.btnCapImg);
        btnRCamera = (Button) findViewById(R.id.btnRcamera);
        btnRCamera.setEnabled(false);

        folderPath = Environment.getExternalStorageDirectory() + "/chidiya";
        uploadfolder = Environment.getExternalStorageDirectory() + "/panchi";

        File dir = new File(folderPath);
        if (dir.isDirectory())
        {
            String[] children = dir.list();
            for (int i = 0; i < children.length; i++)
            {
                new File(dir, children[i]).delete();
            }
        }
        File dire = new File(uploadfolder);
        if (dire.isDirectory())
        {
            String[] childrene = dire.list();
            for (int i = 0; i < childrene.length; i++)
            {
                new File(dire, childrene[i]).delete();
            }
        }
        final File foldere = new File(uploadfolder);
        if (!foldere.exists()) {
            File wallpaperDirectory = new File(uploadfolder);
            wallpaperDirectory.mkdirs();
        }

        final File folder = new File(folderPath);
        if (!folder.exists()) {
            File wallpaperDirectory = new File(folderPath);
            wallpaperDirectory.mkdirs();
        }

        if (checkCameraHardware()) {

            camera = getCameraInstance(cameraType);
            cameraPreview = new CameraPreview(this, camera, cameraType);
            frameCamera.addView(cameraPreview);
            camera.setFaceDetectionListener(new MyFaceDetectionListener());

            setFocus();
            startFaceDetection();
        } else {
            Toast.makeText(getApplicationContext(), "Device not support camera feature", Toast.LENGTH_SHORT).show();
        }

        btnCapImg.setOnClickListener(new View.OnClickListener() {
                                         @Override
                                         public void onClick(View v) {

                                             camera.takePicture(myShutterCallback, null, pictureCallback);
                                             AudioSavePathInDevice = folderPath + "/AUD" + System.currentTimeMillis() + ".mp3";
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
                                             /*
                                             try {
                                                 String h = System.currentTimeMillis() + "";
                                                 // this will create a new name everytime and unique
                                                 File root = new File(folderPath);
                                                 // if external memory exists and folder with name Notes
                                                 if (!root.exists()) {
                                                     root.mkdirs(); // this will create folder.
                                                 }
                                                 File filepath = new File(root, h + ".txt");  // file path to save
                                                 FileWriter writer = new FileWriter(filepath);
                                                 writer.append("latitude " + lat);
                                                 writer.append("\n");
                                                 writer.append("Longitude " + lon);
                                                 writer.append("\n");
                                                 writer.flush();
                                                 writer.close();
                                             } catch (IOException e) {
                                                 e.printStackTrace();
                                             }
*/
                                             //for (int i = 0; i < 1; i++) {
                                             try {
                                                 sleep(5000);
                                             } catch (InterruptedException e) {
                                                 e.printStackTrace();
                                             }
                                             //}
                                             mediaRecorder.stop();
                                             mediaRecorder = null;
                                             //camera.stopPreview();
                                             btnCapImg.setEnabled(false);
                                             btnRCamera.setEnabled(true);
                                             Toast.makeText(CollectorActivity.this, "Saving Data", Toast.LENGTH_LONG).show();

                                         }
                                     }
        );


        btnRCamera.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String k = System.currentTimeMillis()+ "";
                String itemText = (String) Mine.getSelectedItem();
                zipfile = uploadfolder + "/" +itemText+ "_"+lat+ "_"+ lon+ "_" +k +".zip";
                zipFolder(folderPath, uploadfolder + "/" +itemText+ "_"+lat+ "_"+ lon+ "_" +k+".zip");

                if (zipfile != null) {
                    new CollectorActivity.UploadFileToServer().execute();
                }else{
                    Toast.makeText(getApplicationContext(), "Please select a file to upload.", Toast.LENGTH_SHORT).show();
                }
                btnRCamera.setEnabled(false);
            }

            private void zipFolder(String inputFolderPath, String outZipPath) {
                try {
                    FileOutputStream fos = new FileOutputStream(outZipPath);
                    ZipOutputStream zos = new ZipOutputStream(fos);
                    File srcFile = new File(inputFolderPath);
                    File[] files = srcFile.listFiles();
                    Log.d("", "Zip directory: " + srcFile.getName());
                    for (int i = 0; i < files.length; i++) {
                        Log.d("", "Adding file: " + files[i].getName());
                        byte[] buffer = new byte[1024];
                        FileInputStream fis = new FileInputStream(files[i]);
                        zos.putNextEntry(new ZipEntry(files[i].getName()));
                        int length;
                        while ((length = fis.read(buffer)) > 0) {
                            zos.write(buffer, 0, length);
                        }
                        zos.closeEntry();
                        fis.close();
                    }
                    zos.close();
                } catch (IOException ioe) {
                    Log.e("", ioe.getMessage());
                }
            }

        });
    }

    public void setFocus() {
        Camera.Parameters params = camera.getParameters();
        if (params.getSupportedFocusModes().contains(Camera.Parameters.FOCUS_MODE_CONTINUOUS_PICTURE)) {
            params.setFocusMode(Camera.Parameters.FOCUS_MODE_CONTINUOUS_PICTURE);
        } else {
            params.setFocusMode(Camera.Parameters.FOCUS_MODE_AUTO);
        }

        camera.setParameters(params);
    }

    public void startFaceDetection() {
        // Try starting Face Detection
        Camera.Parameters params = camera.getParameters();

        // start face detection only *after* preview has started
        if (params.getMaxNumDetectedFaces() > 0) {
            // camera supports face detection, so can start it:
            camera.startFaceDetection();
        }
    }

    void setCameraZoom(Camera camera) {
        Camera.Parameters parameters = camera.getParameters();
        int zoom = parameters.getMaxZoom();
        parameters.setZoom(5);
        camera.setParameters(parameters);
    }

    private boolean checkCameraHardware() {

        if (getPackageManager().hasSystemFeature(PackageManager.FEATURE_CAMERA)) {
            return true;
        } else {
            return false;
        }
    }

    private Camera getCameraInstance(int cameraType) {
        Camera camera = null;
//        Camera.CameraInfo cameraInfo = new Camera.CameraInfo();
//        for (int i=0;i<Camera.getNumberOfCameras();i++){
//            Camera.CameraInfo camInfo = new Camera.CameraInfo();
//            Camera.getCameraInfo(i, camInfo);
//
//            if (camInfo.facing==(Camera.CameraInfo.CAMERA_FACING_FRONT)) {
        try {
            camera = Camera.open(cameraType);
        } catch (Exception e) {
            Log.d("tag", "Error setting camera not open " + e);
        }
//            }
//        }

        return camera;
    }

    Camera.ShutterCallback myShutterCallback = new Camera.ShutterCallback() {

        @Override
        public void onShutter() {
            // TODO Auto-generated method stub

        }
    };

    class MyFaceDetectionListener implements Camera.FaceDetectionListener {

        @Override
        public void onFaceDetection(Camera.Face[] faces, Camera camera) {
            if (faces.length > 0) {
                Log.d("FaceDetection", "face detected: " + faces.length +
                        " Face 1 Location X: " + faces[0].rect.centerX() +
                        "Y: " + faces[0].rect.centerY());
                Toast.makeText(getApplicationContext(), "face detected: " + faces.length +
                        " Face 1 Location X: " + faces[0].rect.centerX() +
                        "Y: " + faces[0].rect.centerY(), Toast.LENGTH_SHORT).show();
            }
        }
    }

    private Camera.PictureCallback pictureCallback = new Camera.PictureCallback() {
        @Override
        public void onPictureTaken(byte[] data, Camera camera) {

            File file = new File(folderPath + "/IMG" + System.currentTimeMillis() + ".jpg");
            if (file == null) {
                Log.d("tag", "Error creating media file, check storage permissions: ");
                return;
            }

//            int width=getResources().getDisplayMetrics().widthPixels;
//            int hight=getResources().getDisplayMetrics().heightPixels;

            Bitmap bm = BitmapFactory.decodeByteArray(data, 0, (data) != null ? data.length : 0);

            if (getResources().getConfiguration().orientation == Configuration.ORIENTATION_PORTRAIT) {
//                Bitmap scaledBm=Bitmap.createScaledBitmap(bm,width,hight,true);
//                int w=scaledBm.getWidth();
//                int h=scaledBm.getHeight();

                Matrix matrix = new Matrix();
                matrix.setRotate(90);
                bm = Bitmap.createBitmap(bm, 0, 0, bm.getWidth(), bm.getHeight(), matrix, false);

            }

            try {
                FileOutputStream fileOutputStream = new FileOutputStream(file);
                bm.compress(Bitmap.CompressFormat.JPEG, 80, fileOutputStream);
                fileOutputStream.flush();
                fileOutputStream.close();
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
            camera.startPreview();
        }
    };

    @Override
    protected void onPause() {
        super.onPause();
        // if you are using MediaRecorder, release it first
        camera.stopPreview();
    }

    public void MediaRecorderReady() {
        mediaRecorder = new MediaRecorder();
        mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP);
        mediaRecorder.setAudioEncoder(MediaRecorder.OutputFormat.AMR_NB);
        mediaRecorder.setAudioEncodingBitRate(320000);
        mediaRecorder.setAudioSamplingRate(44100);
        mediaRecorder.setOutputFile(AudioSavePathInDevice);
    }

/*
class myLocationListener implements LocationListener{

    @Override
    public void onLocationChanged(Location location) {
        // TODO Auto-generated method stub
        if(location!=null){
            txtLat = (TextView) findViewById(R.id.textview1);
            txtLat.setText("Latitude:" + location.getLatitude() + ", Longitude:" + location.getLongitude());
            lat = location.getLatitude()+"XX";
            lon = location.getLongitude()+"YY";
        }
    }

    @Override
    public void onProviderDisabled(String provider) {
        // TODO Auto-generated method stub

    }

    @Override
    public void onProviderEnabled(String provider) {
        // TODO Auto-generated method stub

    }

    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {
        // TODO Auto-generated method stub

    }

}}
*/

    private class UploadFileToServer extends AsyncTask<String, String, String> {
        @Override
        protected void onPreExecute() {
            sourceFile = new File(zipfile);
            totalSize = (int) sourceFile.length();
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
            String fileName = sourceFile.getName();

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

            } catch (Exception e) {
                // Exception
            } finally {
                if (connection != null) connection.disconnect();
            }
            return null;
        }

        @Override
        protected void onPostExecute(String result) {
            Log.e("Response", "Response from server: " + "UPLOADED Thanks");
            Toast.makeText(getApplicationContext(), result, Toast.LENGTH_SHORT).show();
            super.onPostExecute(result);
        }

    }
    @Override
    public void onBackPressed() {
        Intent intent = new Intent(CollectorActivity.this, MainActivity.class);
        startActivity(intent);
        // Do Here what ever you want do on back press;
    }
}

