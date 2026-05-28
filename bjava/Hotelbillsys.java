package bjava;

public class Hotelbillsys {
    public static void main(String[] args) {
       double roomtarriff = 5000.0;
       int days = 10;
       Double tar = roomtarriff;
       double servicecharge = 150.0;
       Integer d = days;
       Double charges = servicecharge;

       double bill = (tar * d * charges);
       System.out.println("no of days : " + d);
       System.out.println("tar : " + tar);
       System.out.println("charges : " + charges);
       System.out.println("bill : " + bill);

    }
    
}
