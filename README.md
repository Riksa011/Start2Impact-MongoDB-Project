# Start2Impact MongoDB Project

<p align="center">
    <img src="project/apps/exchange/static/icons/bitchange_logo.png" alt="BitChange logo">
</p>

This is my MongoDB project for [Start2Impact](https://talent.start2impact.it/profile/riccardo-santi).

### The main purpose of this project is to build a Bitcoin exchange platform using Django, Djongo and MongoDB.

BitChange allows users to register and log into the platform and gives from 1 to 10 bitcoins and 20'000€ to every new user to start trading.
Customers can post buy or sell orders for a certain amount of Bitcoin at a specific price in €.
The platform matches user orders based on the quantity of Bitcoin and the Euro price, and doesn't charge any fees.

__Django__ is a powerful and popular Python based web framework for building web applications.
<br>
__MongoDB__ is a high-performance NoSQL database that provides flexible and scalable data storage capabilities.
<br>
__Djongo__ is a database connector that allows Django to interact with MongoDB.


<hr/>


## 📖Index

- [ 🚀 Main Features ](#mainfeatures)
- [ 🛠️ How to deploy ](#howtodeploy)
- [ 📈 Improved Skills ](#improvedskills)
- [ 👨‍💻 About me ](#aboutme)



<a name="mainfeatures"></a>
## 🚀 Main Features: 


- #### A page where users can create a new account and then log into the platform
<p align="center">
    <img src="images/2.png" alt="USER REGISTRATION - IMAGE 2">
    <img src="images/3.png" alt="USER LOGIN - IMAGE 3">
    <img src="images/4.png" alt="USER PROFILE - IMAGE 4">
</p>
<br><br>


- #### A dashboard page where users can see their current wallet balance and their total profit & loss
<p align="center">
    <img src="images/5.png" alt="USER ACCOUNT DROPDOWN - IMAGE 5">
    <img src="images/6.png" alt="USER DASHBOARD - IMAGE 6">
</p>
<br><br>


- #### A page where anyone can see the list of open orders not yet matched 
<p align="center">
    <img src="images/7.png" alt="ORDER BOOK - IMAGE 7">
</p>
<br><br>


- #### A page where users can post new orders
<p align="center">
    <h5 align="left">Example of User1 creating a buy order</h5>
    <img src="images/8.png" alt="NEW BUY ORDER - IMAGE 8">
    <img src="images/9.png" alt="BUY ORDER CREATED - IMAGE 9">
    <img src="images/10.png" alt="UPDATED DASHBOARD 1 - IMAGE 10">
    <br><br>
    <h5 align="left">Example of User2 creating a sell order</h5>
    <img src="images/11.png" alt="NEW SELL ORDER - IMAGE 11">
</p>
<br><br>


- #### A page where users can see their orders status
<p align="center">
    <h5 align="left">Example of User1 buy order full match with User2 sell order</h5>
    <img src="images/12.png" alt="USER1 BUY ORDER MATCHED orders - IMAGE 12">
    <img src="images/13.png" alt="USER1 BUY ORDER MATCHED dashboard - IMAGE 13">
    <h5 align="left">Example of User2 sell order partial match with User1 buy order</h5>
    <img src="images/14.png" alt="USER2 SELL ORDER PARTIALLY MATCHED orders - IMAGE 14">
    <img src="images/15.png" alt="USER2 SELL ORDER PARTIALLY MATCHED dashboard - IMAGE 15">
</p>
<br><br>


- #### A page where users can get a Json report of their orders
<p align="center">
    <img src="images/16.png" alt="USER JSON ORDERS REPORT - IMAGE 16">
</p>
<br><br>


- #### A page where users can delete one of their open orders
<p align="center">
    <img src="images/del1.png" alt="USER ORDER DELETE">
    <img src="images/del2.png" alt="ORDER DELETED">
    <img src="images/del3.png" alt="UPDATED DASHBOARD">
</p>
<br><br>


- #### The ability to adapt the website page and content to different types of devices to allow users to have always the best experience
<p align="center">
    <img src="images/one.png" alt="WEBSITE ADAPTATION EXAMPLE 1">
    <img src="images/two.png" alt="WEBSITE ADAPTATION EXAMPLE 2">
</p>
<br><br>



<a name="howtodeploy"></a>
## 🛠️ How to deploy

- Clone this repository in your local
- Be sure to have Python installed on your device, for this project i used Python 3.10.6.
- Be sure to have a Python IDE on board (I recommend [PyCharm](https://www.jetbrains.com/pycharm/))
- Open the program main directory in your IDE, open a new terminal window and type `pip install virtualenv`
- Create a virtual environment by typing `python3.10  -m venv env` and activate it with `source env/bin/activate`
- Install program requirements by typing `pip install -r requirements.txt`
- Update the program MongoDB database by typing `cd Project`, `python manage.py makemigrations` and `python manage.py migrate`
- Run the program by typing `python manage.py runserver`
- Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser and enjoy BitChange!



<a name="improvedskills"></a>
## 📈 Improved Skills
[Python](https://www.python.org/), [Django](https://www.djangoproject.com/), [Djongo](https://github.com/doableware/djongo#readme), [MongoDB](https://www.mongodb.com/), HTML & CSS with [Bootstrap](https://getbootstrap.com/)


<a name="aboutme"></a>
## 👨‍💻 About me
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/riccardo-santi/)
