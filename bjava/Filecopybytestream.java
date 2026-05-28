package bjava;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;

public class Filecopybytestream {
    public static void main(String[] args) {
        
        String soucfile = " source.txt";
        String destfile = " dest.txt";

        try(FileInputStream in = new FileInputStream(soucfile);
    FileOutputStream o = new FileOutputStream(destfile)){
        int bytecontent;

        while((bytecontent = in.read()) !=1 ){
            o.write(bytecontent);
        }

        System.out.println("file copied succesfully");
    }catch(IOException e){
        System.err.println("errodr occured: " + e.getMessage());
    }
    }
    
}
