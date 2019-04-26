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

public class popup extends AppCompatActivity {
    String[] Birds = {"alexandrine_parakeet", "brahamini_myna", "collared_dove", "common_myna", "hoopoe", "house_crow", "indian_peafowl", "indian_robin", "jungle_babbler", "koel", "red_vented_bulbul", "red_whiskered_bulbul", "rock_dove", "rose-ringed_parakeet", "tailor_bird", "yellow_footed_pigeon","not found"};
    Integer[] birpics = {R.drawable.pic1, R.drawable.pic2, R.drawable.pic3, R.drawable.pic4, R.drawable.pic5, R.drawable.pic6crow, R.drawable.pic7, R.drawable.pic8, R.drawable.pic9, R.drawable.pic10, R.drawable.pic11, R.drawable.pic12, R.drawable.pic13, R.drawable.pic14, R.drawable.pic15, R.drawable.pic16, R.drawable.pic0};
    String s = GPSTracker.global.FINALBIRD;
    Integer num = 16;
    String[] url = {"https://en.wikipedia.org/wiki/alexandrine_parakeet",
            "https://en.wikipedia.org/wiki/Brahminy_starling",
            "https://en.wikipedia.org/wiki/collared_dove",
            "https://en.wikipedia.org/wiki/common_myna",
            "https://en.wikipedia.org/wiki/hoopoe",
            "https://en.wikipedia.org/wiki/house_crow",
            "https://en.wikipedia.org/wiki/indian_peafowl",
            "https://en.wikipedia.org/wiki/indian_robin",
            "https://en.wikipedia.org/wiki/jungle_babbler",
            "https://en.wikipedia.org/wiki/koel",
            "https://en.wikipedia.org/wiki/Red-vented_bulbul",
            "https://en.wikipedia.org/wiki/Red-whiskered_bulbul",
            "https://en.wikipedia.org/wiki/rock_dove",
            "https://en.wikipedia.org/wiki/rose-ringed_parakeet",
            "https://en.wikipedia.org/wiki/tailor_bird",
            "https://en.wikipedia.org/wiki/Yellow-footed_green_pigeon"};
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getSupportActionBar().hide();

        setContentView(R.layout.popup);
        for( int i = 0;  i < 16 ; i++){
            if(s.equals(Birds[i])){
                num = i;
            }
        }
        this.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT) );
        Button exit = findViewById(R.id.button);
        ImageView IMGG = findViewById(R.id.imageView);
        TextView ans = findViewById(R.id.bir);
        Button more  = findViewById(R.id.know);
        ans.setText(Birds[num]);
        IMGG.setImageDrawable(getResources().getDrawable(birpics[num]));
        more.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(url[num]));
                startActivity(browserIntent);
            }
        });
        exit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(popup.this, MainActivity.class);
                startActivity(intent);
            }
        });

    }

    @Override
    public void onBackPressed() {
        Intent intent = new Intent(popup.this, MainActivity.class);
        startActivity(intent);
        // Do Here what ever you want do on back press;
    }
}
