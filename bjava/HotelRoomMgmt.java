package bjava; // Ensure your file is in a folder named 'bjava'

class Room {
    private int roomNumber;
    private double basePrice;

    Room(int roomNumber) {
        this.roomNumber = roomNumber;
        this.basePrice = 0.0;
    }

    Room(int roomNumber, double basePrice) {
        this.roomNumber = roomNumber;
        setBasePrice(basePrice);
    }

    public void setBasePrice(double basePrice) {
        if (basePrice >= 0) {
            this.basePrice = basePrice;
        } else {
            System.out.println("Invalid price!");
        }
    }

    public void displayDetails() {
        System.out.println("Room No: " + roomNumber);
        System.out.println("Base Price: " + basePrice);
    }
}

class DeluxeRoom extends Room {
    private boolean hasWifi;
    private boolean includesBreakfast;

    // Changed basePrice to double to match parent
    DeluxeRoom(int roomNumber, double basePrice, boolean hasWifi, boolean includesBreakfast) {
        super(roomNumber, basePrice);
        this.hasWifi = hasWifi;
        this.includesBreakfast = includesBreakfast;
    }

    @Override
    public void displayDetails() {
        super.displayDetails();
        System.out.println("WiFi: " + hasWifi);
        System.out.println("Breakfast: " + includesBreakfast);
    }
}
 
public class HotelRoomMgmt {
    public static void main(String[] args) {
        Room room = new Room(101);
        DeluxeRoom deluxeRoom = new DeluxeRoom(102, 2500.0, true, true);
        
        room.displayDetails();
        System.out.println("---");
        deluxeRoom.displayDetails();
    }
}