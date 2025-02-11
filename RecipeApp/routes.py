from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, abort, json
import requests
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user
from RecipeApp.forms import RegistrationForm, LoginForm, PreferenceForm
from RecipeApp.models import db, User, UserPreference
from bs4 import BeautifulSoup

main = Blueprint("main", __name__)

def extract_instructions_from_url(url):
    """Attempt to scrape cooking instructions from recipe website"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Common CSS selectors for instructions (add more as needed)
        selectors = [
            'div.recipe-instructions',
            'ol.instructions',
            'div.directions',
            'section.recipe-steps',
            '[itemprop="recipeInstructions"]'
        ]
        
        for selector in selectors:
            instructions = soup.select(selector)
            if instructions:
                return '\n'.join([p.get_text(separator='\n', strip=True) for p in instructions])
        
        return "Instructions unavailable - please visit source website"
        
    except Exception as e:
        print(f"Error scraping instructions: {str(e)}")
        return "Could not retrieve instructions. Please view original source."
    

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')


@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    
    if form.validate_on_submit():
        
        # Check if email exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('main.login'))
        
        # Create new user
        new_user = User(email=form.email.data)
        new_user.set_password(form.password.data)
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)


@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)  # Proper login handling
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)


@main.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@main.route("/profile")
@login_required
def profile():
    return render_template('profile.html', 
                         nickname=current_user.email.split('@')[0],
                         email=current_user.email)


@main.route("/recipe/input")
@login_required
def recipe_input():
    return render_template('recipe_input.html')


@main.route("/upload-image")
@login_required
def upload_image():
    return render_template('upload_image.html')  # We'll create this next


# manual_input route
@main.route("/manual-input", methods=['GET', 'POST'])
@login_required
def manual_input():
    if request.method == 'POST':
        try:
            ingredients = json.loads(request.form.get('ingredients', '[]'))
            if not ingredients:
                flash('Please add at least one ingredient', 'warning')
                return redirect(url_for('main.manual_input'))
                
            session['ingredients'] = ingredients
            return redirect(url_for('main.preferences'))
            
        except json.JSONDecodeError:
            flash('Invalid ingredients format', 'danger')
            return redirect(url_for('main.manual_input'))
            
    return render_template('manual_input.html')

@main.route("/api/ingredient-suggestions")
def ingredient_suggestions():
    query = request.args.get('query', '')
    API_KEY = '0ceb03c406e94244a2f5576a172c773d'  # 🔑 Replace with your key
    url = f'https://api.spoonacular.com/food/ingredients/autocomplete?query={query}&number=5&apiKey={API_KEY}'
    response = requests.get(url)
    suggestions = [ingredient['name'] for ingredient in response.json()]
    return jsonify(suggestions)


# RecipeApp/routes.py
@main.route("/preferences", methods=['GET', 'POST'])
@login_required
def preferences():
    form = PreferenceForm()
    saved_prefs = UserPreference.query.filter_by(user_id=current_user.id).all()

    if form.validate_on_submit():
        # Process preferences
        prefs_data = {
            'max_time': form.max_time.data,
            'max_calories': form.max_calories.data if form.max_calories.data else None,
            'diet': form.diet.data if form.diet.data else None,
            'allergies': form.allergies.data if form.allergies.data else []
        }
        
        # Save to DB if requested
        if form.save_preference.data:
            new_pref = UserPreference(
                name=form.preference_name.data or f"My Preference {len(saved_prefs)+1}",
                user_id=current_user.id,
                **prefs_data
            )
            db.session.add(new_pref)
            db.session.commit()
        
        # Store preferences in session
        session['current_prefs'] = prefs_data
        return redirect(url_for('main.recommendations'))
    
    return render_template('preferences.html', form=form, saved_prefs=saved_prefs)


@main.route('/api/load-preference/<int:pref_id>')
@login_required
def load_preference(pref_id):
    pref = UserPreference.query.filter_by(id=pref_id, user_id=current_user.id).first()
    if not pref:
        return jsonify(error="Preference not found"), 404
    
    session['current_prefs'] = {
        'max_time': pref.max_time,
        'diet': pref.diet,
        'allergies': pref.allergies.split(',') if pref.allergies else []
    }
    
    return jsonify(success=True)


# Delete preference
@main.route('/api/delete-preference/<int:pref_id>', methods=['DELETE'])
@login_required
def delete_preference(pref_id):
    pref = UserPreference.query.filter_by(id=pref_id, user_id=current_user.id).first()
    if not pref:
        return jsonify(error="Preference not found"), 404
    
    db.session.delete(pref)
    db.session.commit()
    return jsonify(success=True)

# Save preferences
@main.route('/save-preferences', methods=['POST'])
@login_required
def save_preferences():
    try:
        data = request.get_json()
        
        # Save to database if requested
        if data.get('save_preference'):
            new_pref = UserPreference(
                name=data.get('preference_name'),
                user_id=current_user.id,
                max_time=data.get('max_time'),
                difficulty=data.get('difficulty'),
                diet=data.get('diet'),
                allergies=','.join(data.get('allergies', []))
            )
            db.session.add(new_pref)
            db.session.commit()

        # Store in session
        session['current_prefs'] = {
            'max_time': data.get('max_time'),
            'difficulty': data.get('difficulty'),
            'diet': data.get('diet'),
            'allergies': data.get('allergies', [])
        }

        return jsonify(success=True)

    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500
    

@main.route('/api/load-preference-settings/<int:pref_id>')  # Changed URL
@login_required
def load_preference_settings(pref_id):
    try:
        pref = UserPreference.query.filter_by(id=pref_id, user_id=current_user.id).first()
        if not pref:
            return jsonify(error="Preference not found"), 404
        
        # Store preferences in session
        session['current_prefs'] = {
            'max_time': pref.max_time,
            'diet': pref.diet,
            'allergies': pref.allergies.split(',') if pref.allergies else []
        }
        
        return jsonify(success=True)
    
    except Exception as e:
        return jsonify(error=str(e)), 500


# Recommendations page
@main.route('/recommendations')
@login_required
def recommendations():
    # Get preferences from session or default to empty
    prefs = session.get('current_prefs', {})
    ingredients = session.get('ingredients', [])
    
    if not ingredients:
        flash('Please add some ingredients first', 'warning')
        return redirect(url_for('main.recipe_input'))

    # Edamam API parameters
    params = {
        'q': ' '.join(ingredients),
        'app_id': '0a8c40bf',  # Your Edamam app ID
        'app_key': 'fe725df5d4b1f5da04f725e546c217c4',  # Your Edamam app key
        'type': 'public',
        'from': 0,
        'to': 5
    }

    # Apply preferences
    if prefs:
        # Map allergies to Edamam's health labels
        allergy_mapping = {
            'dairy': 'dairy-free',
            'gluten': 'gluten-free',
            'nuts': 'peanut-free'
        }
        
        if prefs.get('allergies'):
            health_labels = [allergy_mapping[a] for a in prefs['allergies'] if a in allergy_mapping]
            if health_labels:
                params['health'] = health_labels
        
        # Handle cooking time
        if prefs.get('max_time'):
            params['time'] = prefs['max_time']  # Just the number, no range
        
        # Handle diet
        diet_mapping = {
            'vegetarian': 'vegetarian',
            'vegan': 'vegan',
            'gluten-free': 'gluten-free'
        }
        if prefs.get('diet') and prefs['diet'] in diet_mapping:
            params['diet'] = diet_mapping[prefs['diet']]

    try:
        response = requests.get(
            'https://api.edamam.com/api/recipes/v2',
            params=params,
            headers={
                'Accept': 'application/json',
                'Edamam-Account-User': 'jeolsh0704'  # Your Edamam account identifier
            },
            timeout=10
        )
        
        # Handle API errors
        if response.status_code == 400:
            error_detail = response.json().get('message', 'Invalid request parameters')
            flash(f'API Error: {error_detail}', 'danger')
            return redirect(url_for('main.home'))
            
        response.raise_for_status()
        
        data = response.json()
        recipes = []
        
        for hit in data.get('hits', [])[:6]:
            recipe_data = hit.get('recipe', {})
            recipes.append({
                'uri': recipe_data.get('uri', '').split('#')[-1],
                'title': recipe_data.get('label', 'Untitled Recipe'),
                'image': recipe_data.get('image', url_for('static', filename='img/placeholder.jpg')),
                'time': recipe_data.get('totalTime', 0),
                'servings': recipe_data.get('yield', 1),
                'calories': round(recipe_data.get('calories', 0)),
                'ingredients': recipe_data.get('ingredientLines', []),
                'url': recipe_data.get('url', '#'),
                'diet_labels': recipe_data.get('dietLabels', []),
                'health_labels': recipe_data.get('healthLabels', [])
            })

        return render_template('recommendations.html', 
                            recipes=recipes,
                            current_prefs=prefs)
        
    except requests.exceptions.RequestException as e:
        flash(f'Error fetching recipes: {str(e)}', 'danger')
        return redirect(url_for('main.home'))

@main.route('/recipe/<string:recipe_id>')
@login_required
def recipe_detail(recipe_id):
    try:
        # Edamam API call for single recipe
        params = {
            'app_id': '0a8c40bf',
            'app_key': 'fe725df5d4b1f5da04f725e546c217c4',
            'type': 'public'
        }
        
        headers = {
            'Accept': 'application/json',
            'Edamam-Account-User': 'jeolsh0704'  # Your account identifier
        }

        response = requests.get(
            f'https://api.edamam.com/api/recipes/v2/{recipe_id}',
            params=params,
            headers=headers,
            timeout=20
        )
        
        if response.status_code == 404:
            flash('Recipe details not found', 'warning')
            return redirect(url_for('main.recommendations'))
            
        response.raise_for_status()
        
        recipe_data = response.json().get('recipe', {})
        
        # Process recipe data
        recipe = {
            'title': recipe_data.get('label', 'Untitled Recipe'),
            'image': recipe_data.get('image', url_for('static', filename='img/placeholder.jpg')),
            'time': recipe_data.get('totalTime', 0),
            'servings': recipe_data.get('yield', 1),
            'calories': round(recipe_data.get('calories', 0)),
            'ingredients': recipe_data.get('ingredientLines', []),
            'instructions': extract_instructions_from_url(recipe_data.get('url', '')),
            'diet_labels': recipe_data.get('dietLabels', []),
            'health_labels': recipe_data.get('healthLabels', []),
            'source_url': recipe_data.get('url', '#')
        }
        
        return render_template('recipe_detail.html', recipe=recipe)
        
    except requests.exceptions.RequestException as e:
        flash('Error fetching recipe details', 'danger')
        return redirect(url_for('main.recommendations'))
    
@main.route('/api/detect-ingredients', methods=['POST'])
@login_required
def detect_ingredients():
    if 'image' not in request.files:
        return jsonify(error="No image provided"), 400
    
    image = request.files['image']
    if image.filename == '':
        return jsonify(error="No image selected"), 400
    
    # Send image to Imagga API
    try:
        imagga_url = "https://api.imagga.com/v2/tags"
        response = requests.post(
            imagga_url,
            files={'image': image},
            auth=('acc_133549f38b4202e', '4faf211ee7d19c02e1217f4d2bb3087c')
        )
        response.raise_for_status()
        tags = response.json().get('result', {}).get('tags', [])
        ingredients = [tag['tag']['en'] for tag in tags[:10]]  # Top 10 tags
        return jsonify(ingredients=ingredients)
    except Exception as e:
        return jsonify(error=str(e)), 500