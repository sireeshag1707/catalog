# Item Catalog Gadget Hub Web App
By sireesha Goutham
This web app is a project for the Udacity [FSND Course](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).


## In This Project
 Three Python files are their 
 main.py
 Data_Setup.py
 data_init.py
 And HTML Files are Placed in the Templates folder by using the Flask Applocation

## Skills Required
1. Python
2. HTML
3. CSS
4. OAuth2client
5. Flask Framework
6. DataBaseModels


## Dependencies
- [Vagrant](https://www.vagrantup.com/)
- [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)



## How to Install
1. Install Vagrant & VirtualBox
2. Clone the Udacity Vagrantfile
3. Go to Vagrant directory and either clone this repo or download and place zip here
3. Launch the Vagrant VM (`vagrant up`)
4. Log into Vagrant VM (`vagrant ssh`)
5. Navigate to `cd /vagrant` as instructed in terminal
6. The app imports requests which is not on this vm. Run pip install requests
7. Setup application database `python /Gadget Hub/Data_Set.py`
8. Insert sample data `python /Gadget Hub/data_init.py`
9. Run application using `python /Gadget Hub/project.py`
10.Access the application locally using http://localhost:5555


### JSON Codes
The following are open to the public:

1.Gadget Catalog JSON: `/GadgetStore/JSON`
    - Displays the whole Gadget models catalog. Gadget Categories and all models.

2.Gadget Categories JSON: `/GadgetStore/GadgetCategories/JSON`
    - Displays all Gadget categories
3.All Gadget Editions: `/GadgetStore/Gadget/JSON`
	- Displays all Gadget Models

4.Gadget Edition JSON: `/GadgetStore/<path:Gadget_name>/Gadget/JSON`
    - Displays Gadget models for a specific Gadget category

5.Gadget Category Edition JSON: `/GadgetStore/<path:Gadget_name>/<path:edition_name>/JSON`
    - Displays a specific Gadget category Model.

## Miscellaneous

This project is inspiration from https://github.com/YVenkatesh7/catalog/blob/master/catalog
