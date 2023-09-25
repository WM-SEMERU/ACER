class Vehicle{
    public String brand;
    public String model;
    public String type;
    public int gas_tank_size;
    public int fuel_level;

    public Vehicle(String brand, String model, String type){
        this.brand = brand;
        this.model = model;
        this.type = type;
        this.gas_tank_size = 14;
        this.fuel_level = 0;
    }
    
    public void fuel_up(){
        this.fuel_level = this.gas_tank_size;
        System.out.println("Gas tank is now full");
        read_to_drive();
    }
    public void drive(){
        System.out.println("The " + this.model + " is now driving");
    }
    public boolean read_to_drive(){
        if(this.fuel_level == this.gas_tank_size){
            drive();
            return true;
        }
        else return false;   
    }
    public void check_brand(){
        Automaker maker = new Automaker();
        this.brand = maker.get_brand();
        System.out.println(brand);
    }

    public static void main(String[] args){
        Vehicle car = new Car("Honda", "Accord", "sedan");
        car.check_brand();
        car.fuel_up();
    }
}
class Automaker{
    Vehicle car;
    public Automaker(){
        this.car = null;
    }
    public String get_brand(Vehicle car){
        if (car.brand.equals("Honda")){
            System.out.println("Car is made from Japanese Automaker");
            return "Japan";
        }
        return null;
    }
}