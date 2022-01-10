from itertools import count
from os import error, name
import re
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
app.secret_key='super_secret'
class Shipment_Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Shipment %r>' % self.name

class Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(scale=2), nullable=False)
    count = db.Column(db.Integer)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
       return '<Item %r>' % self.id


@app.route('/delete/<int:id>')
def delete(id):
    item_to_del = Item.query.get_or_404(id)
    try:
        db.session.delete(item_to_del)
        db.session.commit()
        return redirect('/')
    except:
        return 'Error deleteing item'        


@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    item_to_update = Item.query.get_or_404(id)
    if request.method == 'POST':
        item_to_update.name = request.form['name']
        item_to_update.price = request.form['price']
        item_to_update.count = request.form['count']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return render_template("error.html")

    else:
        return render_template('update_item.html', item=item_to_update)

@app.route('/ship_delete/<int:id>')
def ship_delete(id):
    item_to_del = Shipment_Item.query.get_or_404(id)
    try:
        db.session.delete(item_to_del)
        db.session.commit()
        return redirect('/ship')
    except:
        return 'Error deleteing item'        



@app.route('/ship', methods=['POST','GET'])
def ship():
    ship_list = Shipment_Item.query.order_by(Shipment_Item.date_created).all()

    inventory = Item.query.order_by(Item.date_created).all()
    if request.method == 'POST':
        ship_list = request.form.getlist('ship')
        print(ship_list)
        for item in ship_list:
            new_ship_item = Shipment_Item(name=item)
            try:
                db.session.add(new_ship_item)
                db.session.commit()
            except:
                return render_template("error.html")
        
        return redirect('/ship')
    else: 
        return render_template("shipment.html", items=inventory, shipment=ship_list) 


@app.route('/shipout', methods=['GET', 'POST'])
def shipout():
    ship_list = Shipment_Item.query.order_by(Shipment_Item.date_created).all()
    if request.method == 'POST':
        for item in range(len(ship_list)):
            item_to_ship = ship_list[item]

            db.session.delete(item_to_ship)
            db.session.commit()
        
        flash("Shipment sent out!")
        return redirect('/ship')             
    else:
        return redirect('/ship')  


@app.route("/", methods=['GET', 'POST'])
def home():
    inventory = Item.query.order_by(Item.date_created).all()

    if request.method == 'POST':
       item_name = request.form['name']
       item_price = request.form['price']
       item_count = request.form['count']

       # Logic for if an item was already created 
       for item in inventory:
           if (item_name == item.name) and (int(item_price) == item.price):
               item.count = int(item_count) + item.count
               try:
                db.session.commit()
                return redirect('/')
               except:
                   return 'Error adding object to database'
            

       new_item = Item(name=item_name, price=item_price, count=item_count) 
    
       try:
           db.session.add(new_item)
           db.session.commit()
           return redirect('/')
       except:
            return render_template("error.html")
    else:
        return render_template("index.html", items=inventory)
    


if __name__ == '__main__':
    app.run(debug=True)    