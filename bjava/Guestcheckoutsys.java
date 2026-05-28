package bjava;
import java.util.*;

class invalidstayexception extends Exception{
    public invalidstayexception(String message){
        super(message);
    }
}

class Guest{
    private String gname;
    private int daysstayed;
    private double rateperday;

    public Guest(String gname , int daysstayed , double rateperday) throws invalidstayexception{
        if(daysstayed < 1){
            throw new invalidstayexception("invalid no of days stayed");
        }
        this.gname = gname;
        this.daysstayed = daysstayed;
        this.rateperday = rateperday;
    }

    double calculateTotalBill(){
            return daysstayed*rateperday;
    }
} 
public class Guestcheckoutsys {
    public static void main(String[] args) {
        Scanner s = new Scanner(System.in);
        try {
            System.out.print("Enter guest name: ");
            String name = s.nextLine();

            System.out.print("Enter days stayed: ");
            int days = s.nextInt();

            System.out.print("Enter rate per day: ");
            double rate = s.nextDouble();

            Guest g = new Guest(name, days, rate);
            double bill = g.calculateTotalBill();

            System.out.println("Guest: " + name);
            System.out.println("Total Bill: " + bill);

        } catch (invalidstayexception e) {
            System.err.println(e.getMessage());
        } catch (Exception e) {
            System.out.println("Error occurred");
        } finally {
            s.close();
        }
    }
    
}
