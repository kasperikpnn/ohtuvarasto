import os
from flask import Flask, render_template, request, redirect, url_for, flash
from varasto import Varasto

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Store warehouses in memory with names
warehouses = {}
warehouse_counter = 0


@app.route('/')
def index():
    """Display all warehouses"""
    return render_template('index.html', warehouses=warehouses)


@app.route('/warehouse/create', methods=['GET', 'POST'])
def create_warehouse():
    """Create a new warehouse"""
    global warehouse_counter
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        try:
            capacity = float(request.form.get('capacity', 0))
            initial_stock = float(request.form.get('initial_stock', 0))
        except ValueError:
            flash('Invalid numbers! Please enter valid numbers for capacity and stock.', 'error')
            return render_template('create_warehouse.html')

        if not name:
            flash('Please enter a warehouse name!', 'error')
            return render_template('create_warehouse.html')

        if capacity <= 0:
            flash('Capacity must be greater than 0!', 'error')
            return render_template('create_warehouse.html')

        if initial_stock < 0:
            flash('Initial stock cannot be negative!', 'error')
            return render_template('create_warehouse.html')

        if initial_stock > capacity:
            flash('Initial stock cannot exceed capacity!', 'error')
            return render_template('create_warehouse.html')

        warehouse_counter += 1
        warehouse_id = warehouse_counter
        warehouses[warehouse_id] = {
            'name': name,
            'varasto': Varasto(capacity, initial_stock)
        }
        flash(f'Warehouse "{name}" created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('create_warehouse.html')


@app.route('/warehouse/<int:warehouse_id>')
def view_warehouse(warehouse_id):
    """View a specific warehouse"""
    if warehouse_id not in warehouses:
        flash('Warehouse not found!', 'error')
        return redirect(url_for('index'))

    warehouse = warehouses[warehouse_id]
    return render_template('view_warehouse.html', warehouse_id=warehouse_id, warehouse=warehouse)


@app.route('/warehouse/<int:warehouse_id>/edit', methods=['GET', 'POST'])
def edit_warehouse(warehouse_id):
    """Edit warehouse name"""
    if warehouse_id not in warehouses:
        flash('Warehouse not found!', 'error')
        return redirect(url_for('index'))

    warehouse = warehouses[warehouse_id]

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Please enter a warehouse name!', 'error')
        else:
            warehouse['name'] = name
            flash(f'Warehouse renamed to "{name}"!', 'success')
            return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    return render_template('edit_warehouse.html', warehouse_id=warehouse_id, warehouse=warehouse)


@app.route('/warehouse/<int:warehouse_id>/add', methods=['POST'])
def add_to_warehouse(warehouse_id):
    """Add items to warehouse"""
    if warehouse_id not in warehouses:
        flash('Warehouse not found!', 'error')
        return redirect(url_for('index'))

    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        flash('Invalid amount! Please enter a valid number.', 'error')
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    if amount <= 0:
        flash('Amount must be greater than 0!', 'error')
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    warehouse = warehouses[warehouse_id]
    available_space = warehouse['varasto'].paljonko_mahtuu()

    if amount > available_space:
        flash(f'Not enough space! Only {available_space:.2f} units available.', 'warning')
        warehouse['varasto'].lisaa_varastoon(amount)  # Will fill to capacity
    else:
        warehouse['varasto'].lisaa_varastoon(amount)
        flash(f'Added {amount:.2f} units to the warehouse!', 'success')

    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/remove', methods=['POST'])
def remove_from_warehouse(warehouse_id):
    """Remove items from warehouse"""
    if warehouse_id not in warehouses:
        flash('Warehouse not found!', 'error')
        return redirect(url_for('index'))

    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        flash('Invalid amount! Please enter a valid number.', 'error')
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    if amount <= 0:
        flash('Amount must be greater than 0!', 'error')
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    warehouse = warehouses[warehouse_id]
    current_stock = warehouse['varasto'].saldo

    if amount > current_stock:
        flash(f'Not enough stock! Only {current_stock:.2f} units available.', 'warning')

    removed = warehouse['varasto'].ota_varastosta(amount)
    flash(f'Removed {removed:.2f} units from the warehouse!', 'success')

    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/delete', methods=['POST'])
def delete_warehouse(warehouse_id):
    """Delete a warehouse"""
    if warehouse_id not in warehouses:
        flash('Warehouse not found!', 'error')
        return redirect(url_for('index'))

    name = warehouses[warehouse_id]['name']
    del warehouses[warehouse_id]
    flash(f'Warehouse "{name}" deleted!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)
