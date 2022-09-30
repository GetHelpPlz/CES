import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

def initialize_firestore():
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]  = "cdbp-19b07-firebase-adminsdk-vsw0f-b50e28a7c3.json"

    # Use the application default credentials.  The projectID is obtianed 
    # by going to Project Settings and then General.
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'cdbp-19b07',
    })

    # Get reference to database
    db = firestore.client()
    return db

def add_new_plan(db):
    '''
    Prompt the user for a new item to add to the inventory database.  The
    item name must be unique (firestore document id).  
    '''

    title = input("Title: ")
    target = input("Target: ")
    progress = input("Is it finish?: ") #(Finish/Unfinish)
    prt = int(input("Priority: "))

    # Check for an already existing item by the same name.
    # The document ID must be unique in Firestore.
    result = db.collection("inventory").document(title).get()
    if result.exists:
        print("Title already exists!")
        return

    # Build a dictionary to hold the contents of the firestore document.
    data = {"target" : target, "progress" : progress,"prt" : prt}
    db.collection("inventory").document(title).set(data) 

    # Save this in the log collection in Firestore       
    log_transaction(db, f"Added {title} with initial quantity {prt}")

def edit_plan(db):
    '''
    Prompt the user to add quantity to an already existing item in the
    inventory database.  
    '''

    title = input("Title: ")
    new_trt = input("New Target: ")
    new_prog = input("Progress: ")

    # Check for an already existing item by the same name.
    # The document ID must be unique in Firestore.
    result = db.collection("inventory").document(title).get()
    if not result.exists:
        print("Plan does not exist!")
        return

    # Convert data read from the firestore document to a dictionary
    data = result.to_dict()

    # Update the dictionary with the new quanity and then save the 
    # updated dictionary to Firestore.
    data["target"] = new_trt
    data["progress"] = new_prog
    db.collection("inventory").document(title).set(data)

    # Save this in the log collection in Firestore
    log_transaction(db, f"Added {new_trt} {title}")
    
def delete_plan(db):
    '''
    Prompt the user to add quantity to an already existing item in the
    inventory database.  
    '''

    title = input("Title: ")

    # Check for an already existing item by the same name.
    # The document ID must be unique in Firestore.
    result = db.collection("inventory").document(title).get()
    if not result.exists:
        print("Plan does not exist!")
        return

    # Convert data read from the firestore document to a dictionary
    data = result.to_dict()

    # Update the dictionary with the new quanity and then save the 
    
    db.collection("inventory").document(title).delete()
    # updated dictionary to Firestore.


    # Save this in the log collection in Firestore

def search_plan(db):
    '''
    Search the database in multiple ways.
    '''

    print("Select Query")
    print("1) Show All plan")        
    print("2) Show Unfinished plan")
    print("3) Show Finished plan")
    choice = input("> ")
    print()

    # Build and execute the query based on the request made
    if choice == "1":
        results = db.collection("inventory").get()
    elif choice == "2":
        results = db.collection("inventory").where("progress","==","Unfinish").get()
    elif choice == "3":
        results = db.collection("inventory").where("progress","==","Finish").get()
    else:
        print("Invalid Selection")
        return
    
    # Display all the results from any of the queries
    print("")
    print("Search Results")
    print(f"{'Title':<10}  {'Target':<30}  {'Progress':<10}  {'Priority':<10}")
    for result in results:
        item = result.to_dict()
        print(f"{result.id:<10}  {item['target']:<30}  {str(item['progress']):<10}  {item['prt']:<10}")
    print()    

def log_transaction(db, message):
    '''
    Save a message with current timestamp to the log collection in the
    Firestore database.
    '''
    data = {"message" : message, "timestamp" : firestore.SERVER_TIMESTAMP}
    db.collection("log").add(data)    



def main():
    db = initialize_firestore()
    choice = None
    while choice != "0":
        print()
        print("0) Exit")
        print("1) Add New Plan")
        print("2) Edit Plan")
        print("3) Delete Plan")
        print("4) Search Plan")
        choice = input(f"> ")
        print()
        if choice == "1":
            add_new_plan(db)
        elif choice == "2":
            edit_plan(db)
        elif choice == "3":
            delete_plan(db)
        elif choice == "4":
            search_plan(db)                        

if __name__ == "__main__":
    main()