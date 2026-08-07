import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

#Window creation
app = ctk.CTk()
app.title("BMI CALCULATOR")
app.geometry("600x700")
app.resizable(False, False)

app.iconbitmap('logo.ico')
app.configure(fg_color='pink')


#widgets
main_frame = ctk.CTkFrame(  
    app, 
    width=500, 
    height=500, 
    fg_color=['#E6F7FF', '#BFEAFF'],
    corner_radius=20,

 )

main_frame.pack(
    pady=10
)

image1 = Image.open('bmichat.jpg')
image1 = image1.resize((300, 200))
image1 =ImageTk.PhotoImage(image1)

image_label = ctk.CTkLabel(
    app,
    text='',
    image=image1,
)
    
image_label.pack(pady=10)

#heading

header_label = ctk.CTkLabel(
    app,
    text='BMI CALCULATOR',
    text_color='#000080',
    font=('Poppins', 30, 'bold'),
    bg_color='Light Blue',
    fg_color='#FFE5B4',
)

header_label.place(
    x=180,
    y=50
)

cat_frame= ctk.CTkLabel(
    app,
    width=400,
    height=80,
    corner_radius=10,
    text='Feedback (:',
    anchor='center',
    bg_color='lightblue',
    text_color='white',
    font=('poppings', 20 ,'bold')
)
cat_frame.place(x=100, y=180)

#display area

display_label = ctk.CTkLabel(
    app,
    text="",
    font=('Halvetica',15,'bold'),
    text_color='black' ,
    corner_radius=20, 
    width=110,
    height=80,
    bg_color='lightblue',
    fg_color='white'
    )
display_label.place(x=240, y=98)

Height_entry = ctk.CTkEntry(
    app, 
    placeholder_text ='Enter Height(cm)',
    bg_color='dark blue',
    height=30
    )

Height_entry.place(x=140, y=290)

weight_entry = ctk.CTkEntry(
    app, 
    placeholder_text ='Enter weight(kg)',
    bg_color='dark blue',
    height=30
)

weight_entry.place(x=300, y=290)

#app logic

def bmi_calculator():
    #bmi = weight/(height**2)
    try:
        weight = float(weight_entry.get())
        height = float(Height_entry.get())
    except:
        ValueError,ZeroDivisionError(
            cat_frame.configure(text='INVALID INPUT\nNUMBER ONLY',
                                text_color ='red'),
            display_label.configure(text='):',text_color='red')

        )


    bmi = weight/(height**2)
    height = ((height / 100) ** 2)  #divide by 100 to convert cm to m
    bmi = weight / height

    display_label.configure(text= f'BMI SCORE:\n{bmi:.2f}')
    if bmi < 18.5:
        cat_frame.configure(
            text= 'UNDERWEIGHT\nYou need to take your diet seriously'
        ),
        display_label.configure(fg_color ='blue')

    elif 18.5 <= bmi < 25:
        cat_frame.configure(
            text= "NORMAL\nYou're healthy"
        ),
        display_label.configure(fg_color ='green')
    elif 25 <= bmi < 30:
        cat_frame.configure(
            text= 'OVERWEIGHT\nYou need to balance your diet'
        ),
        display_label.configure(fg_color ='orange')
    else:
        cat_frame.configure(
            text= 'OBESE\n You need to see a Doctor'
        ),
        display_label.configure(fg_color ='red')


def reset_bmi():
    Height_entry.delete(0, 'end',)
    weight_entry.delete(0, 'end')
    display_label.configure(text='',fg_color='white')
    cat_frame.configure(text='Feedback (:',text_color='black')
    Height_entry.configure(placeholder_text='Enter Height(cm)', text_color='black')
    weight_entry.configure(placeholder_text='Enter weight(kg)', text_color='black')
 
#buttons

button = ctk.CTkButton(
    app, 
    text='SUBMIT', 
    width=140, 
    height=28, 
    command=bmi_calculator,
    bg_color='light blue' 
    )
button.place(x=210, y=340)

button_reset = ctk.CTkButton(
    app, 
    text='RESET', 
    width=140, 
    height=28,
    bg_color='light blue',
    command=reset_bmi
    )
button_reset.place(x=210, y=370)


app.mainloop()