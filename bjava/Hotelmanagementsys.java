package bjava;



class Hotel{
    private int availroom;
    private int totalroom;

    public Hotel(int totalroom){
        this.availroom=totalroom;
        this.totalroom = availroom;
    }

    public synchronized void bookroom(String cname){
        while(availroom == 0 ){
            try{
                System.out.println(cname + "ios waitintg.., no room avail");
                wait();
            }catch(InterruptedException e){
                Thread.currentThread().interrupt();
            }
        }
        availroom--;
        System.out.println(cname+"booked a room , rooms left: " + availroom);

    }

    public synchronized void releaseroom(String cname){
        if(availroom<totalroom){
            availroom++;
            System.out.println(cname + "cstoemr relaesed rooom , rooms left: " + availroom);
            notifyAll();
            
        }
    }
}

public class Hotelmanagementsys {
    public static void main(String[] args) {
        Hotel myhotel = new Hotel(2);

        Runnable booking = () ->{
            String name = Thread.currentThread().getName();
            myhotel.bookroom("bhavya");

        };

        Runnable release = ()->{
            String name = Thread.currentThread().getName();
            try{
                Thread.sleep(2000);
                myhotel.releaseroom("bhavya");
            }catch (InterruptedException e){
                e.printStackTrace();
            }
        };

        Thread c1 = new Thread(booking,"customer 1");
        Thread c2 = new Thread(booking, "customer 2");
        Thread c3 = new Thread(booking , " cutomer-3");
        Thread c4 = new Thread(booking , "cusomer-4");

        Thread e1 = new Thread(release , " customer -1");
        Thread r2 = new Thread(release, "customer-2");

        c1.start();
        c2.start();
        c3.start();
        c4.start();
        e1.start();
        r2.start();
    }
    
}
