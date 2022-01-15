from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# initalize application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
app.secret_key='super_secret'

# initialize database
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
    # delete the item from the database
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
    # get the data to change, and update database
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

@app.route('/ship', methods=['POST','GET'])
def ship():
    shipmentComplete = False
    inventory = Item.query.order_by(Item.date_created).all()

    if request.method == 'POST':
        ids = request.form.getlist('ship')
        ship_counts = request.form.getlist('ship_count')

        if ship_counts is None:
            return redirect('/ship')

        # handle the sending out a shipment
        for id in ids:
            item_to_ship = Item.query.get_or_404(id)

            item_to_ship.count = item_to_ship.count - int(ship_counts[(int(id)-1)])
            if item_to_ship.count < 0:
                return render_template("error.html")

            if item_to_ship.count == 0:
                db.session.delete(item_to_ship)    
            try:
                db.session.commit()
                shipmentComplete = True
            except:
                return render_template("error.html")    

        if shipmentComplete:
            flash("Your shipment has been shipped out.")

        return redirect('/ship')
    else: 
        return render_template("shipment.html", items=inventory) 

@app.route("/", methods=['GET', 'POST'])
def home():
    # get inventroy to display
    inventory = Item.query.order_by(Item.date_created).all()

    if request.method == 'POST':
       item_name = request.form['name']
       item_price = request.form['price']
       item_count = request.form['count']
       
       # handling blank forms
       if not item_price or not item_count or not item_name:
           return redirect('/')

       # handling zero  
       if int(item_price) == 0 or int(item_count) == 0:
           
           return redirect('/') 

       # logic for if an item was already created
       # we want to add it to the existing item 
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
