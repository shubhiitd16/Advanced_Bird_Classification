package com.example.sandeshsen.lagbhag_hogya;


import android.content.Intent;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import java.io.File;


import static com.example.sandeshsen.lagbhag_hogya.GPSTracker.global.imgpathp;

public class imgpopup extends AppCompatActivity{

    int numi;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getSupportActionBar().hide();

        numi = 35;
        String[] birds = { "Brahminy_maina", "Bulbul", "Collared_dove", "Common_myna",
                "Common_sparrow", "Coppersmith", "Crow_pheasant", "Drongo",
                "Golden_backed_woodpecker", "Green Barbet", "Hoopoe", "House_Crow",
                "Indian_hornbill", "Indian_robin", "Jungle_Crow", "Jungle_babbler",
                "Koel", "Little_green_beeeater", "Magpie_robin", "Owlet",
                "Parakeet", "Pariah_kite", "Partridge", "Peacock", "Pied_myna",
                "Pied_wagtail", "Pigeon", "Pond_heron", "Red_wattled_lapwing",
                "Rufous_backed_shrike", "Shikra", "Sunbird", "Tailor_bird",
                "White_breasted_kingfisher", "White_breasted_water_hen"," Not Found"};

        final String[] x = new String[]{"https://en.wikipedia.org/wiki/Brahminy_sterling",
                "https://en.wikipedia.org/wiki/Bulbul",
                "https://en.wikipedia.org/wiki/Collared_dove",
                "https://en.wikipedia.org/wiki/Common_myna",
                "https://en.wikipedia.org/wiki/House_sparrow",
                "https://en.wikipedia.org/wiki/Coppersmith",
                "https://en.wikipedia.org/wiki/Crow_pheasant",
                "https://en.wikipedia.org/wiki/Drongo",
                "https://en.wikipedia.org/wiki/Black-rumped_flameback",
                "https://en.wikipedia.org/wiki/Green_Barbet",
                "https://en.wikipedia.org/wiki/Hoopoe",
                "https://en.wikipedia.org/wiki/House_Crow",
                "https://en.wikipedia.org/wiki/Indian_grey_hornbill",
                "https://en.wikipedia.org/wiki/Indian_robin",
                "https://en.wikipedia.org/wiki/Jungle_Crow",
                "https://en.wikipedia.org/wiki/Jungle_babbler",
                "https://en.wikipedia.org/wiki/Koel",
                "https://en.wikipedia.org/wiki/Green_bee-eater",
                "https://en.wikipedia.org/wiki/Magpie_robin",
                "https://en.wikipedia.org/wiki/Owlet",
                "https://en.wikipedia.org/wiki/Parakeet",
                "https://en.wikipedia.org/wiki/Pariah_kite",
                "https://en.wikipedia.org/wiki/Partridge",
                "https://en.wikipedia.org/wiki/Peacock",
                "https://en.wikipedia.org/wiki/Pied_myna",
                "https://en.wikipedia.org/wiki/Pied_wagtail",
                "https://en.wikipedia.org/wiki/Pigeon",
                "https://en.wikipedia.org/wiki/Pond_heron",
                "https://en.wikipedia.org/wiki/Red-wattled_lapwing",
                "https://en.wikipedia.org/wiki/Long-tailed_shrike",
                "https://en.wikipedia.org/wiki/Shikra",
                "https://en.wikipedia.org/wiki/Sunbird",
                "https://en.wikipedia.org/wiki/Tailor_bird",
                "https://en.wikipedia.org/wiki/White_breasted_kingfisher",
                "https://en.wikipedia.org/wiki/White-breasted_waterhen",
        "https://www.google.com/"};
        setContentView(R.layout.imgpop);
        String s = GPSTracker.global.FINALBIRDimg;
        String[] k = s.split("found  ");
        for( int i = 0;  i < 35 ; i++){
            if(k[1].equals(birds[i])){
                numi = i;
            }
        }
        this.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT) );
        Button exit = findViewById(R.id.button);
        ImageView IMGG = findViewById(R.id.imageView);
        TextView ans = findViewById(R.id.bir);
        Button more  = findViewById(R.id.know);
        IMGG.setImageURI(Uri.fromFile(new File(imgpathp)));
        ans.setText(birds[numi]);

        more.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(x[numi]));
                startActivity(browserIntent);
            }
        });
        exit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(imgpopup.this, MainActivity.class);
                startActivity(intent);
            }
        });

    }
    @Override
    public void onBackPressed() {
        Intent intent = new Intent(imgpopup.this, MainActivity.class);
        startActivity(intent);
        // Do Here what ever you want do on back press;
    }
}
