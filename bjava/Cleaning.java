package bjava;

import java.util.Scanner;

interface HotelService {
    void performService();
    void displayServiceDetails();
}

class InvalidRoomExceptions extends Exception {
    public InvalidRoomExceptions(String message) {
        super(message);
    }
}

class CleaningService implements HotelService {
    private int roomno;
    private String cleanername;

    public CleaningService(int roomno, String cleanername) throws InvalidRoomExceptions {
        if (roomno < 5 || roomno > 500) {
            throw new InvalidRoomExceptions("Error: Room " + roomno + " out of range");
        }

        this.roomno = roomno;
        this.cleanername = cleanername;
    }

    @Override
    public void performService() {
        System.out.println("Cleaning in progress for room: " + roomno);
    }

    @Override
    public void displayServiceDetails() {
        System.out.println("Cleaner for room " + roomno + " is: " + cleanername);
    }
}

public class Cleaning {
    public static void main(String[] args) {
        Scanner scn = new Scanner(System.in);

        try {
            System.out.print("Enter room no: ");
            int rno = scn.nextInt();
            scn.nextLine();

            System.out.print("Enter cleaner name: ");
            String name = scn.nextLine();

            CleaningService service = new CleaningService(rno, name);
            service.performService();
            service.displayServiceDetails();
        } catch (InvalidRoomExceptions e) {
            System.out.println(e.getMessage());
        } catch (Exception e) {
            System.out.println("An unexpected error has occurred");
        } finally {
            scn.close();
        }
    }
}
