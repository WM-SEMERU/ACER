#include <iostream>
#include <string>

using namespace std;

/* The following test case replicates
*  the vehicle test cases from the other
*  languages */

// TODO: fix Automaker and Vehicle classes
// so Vehicle can call Automaker
// Only fuel_up method is working right now.

class Vehicle;
class Automaker;


class Vehicle
{
    public:
        string brand;
        string model;
        string type;
        int year;
        int gasTankSize;
        int fuelLevel;

        Vehicle(string brand, string model, string type)
        {
            this->brand = brand;
            this->model = model;
            this->type = type;
        }

        void fuel_up()
        {
            fuelLevel = gasTankSize;
            cout << "Gas tank is now full" << endl;
            this -> read_to_drive();
        }

        bool read_to_drive()
        {
            if (fuelLevel == gasTankSize)
            {
                this -> drive();
                return true;
            }
            else {return false;}
        }

        void drive()
        {
            cout << "The " + model + " is now driving." << endl;
        }

        void check_brand()
        {
            Automaker maker;
            brand = maker.get_brand(this);
            cout << brand << endl;
        }


};

class Automaker
{
    public:
        Vehicle car;

    Automaker();

    string get_brand(Vehicle *car)
    {
        if (car->brand.compare("Honda"))
        {
            cout << "Car is made from Japanese automaker" << endl;
            return "Japan";
        }
    }
};




int main()
{
    Vehicle car = Vehicle("Honda","Accord","sedan");
    //car.check_brand();
    car.fuel_up();
}