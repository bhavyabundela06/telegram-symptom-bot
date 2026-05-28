package bjava;


enum RoomType{

    STANDARD(1000) , DELUXE(2500) , SUITE(4000);
 
    private int basetarriff;
    RoomType(int tarriff){
        this.basetarriff = tarriff;
    }

    public int getbasetarriff(){
        return basetarriff;
    }

    public int calcbil(int days){
        return basetarriff*days;
    }
}
public class hotelmgmtss {
    public static void main(String[] args) {
        RoomType selroom = RoomType.DELUXE;
        int staydu = 5;
        int totalCost = selroom.calcbil(staydu);
        System.out.println("enter rooom : " + selroom);
        
        System.out.println("bill : " + totalCost);

    }
    
}
