library(shiny)
library(e1071)
library(ggplot2)

# Load the datasets
heart_data <- read.csv("HeartDisease.csv")
diabetes_data <- read.csv("DiabetesData.csv")

# Train the Naive Bayes models
heart_model <- naiveBayes(num ~ Age + Sex + chesp.pain.type + resting.bp + cholestrol + fasting.blood.sugar + 
                            electrocardiographic + maximum.heart.rate + exercise.induced.angina + oldpeak + slope.of.peak.exercise + 
                            ca + thal, data = heart_data)

diabetes_model <- naiveBayes(class ~ times.pregnant + plasma.glucose + diastolic.bp + triceps.skin + serium.insuline + bmi + diabetes.pedigree + age, 
                             data = diabetes_data)

# Define UI
ui <- fluidPage(
  titlePanel("Disease Prediction"),
  
  sidebarLayout(
    sidebarPanel(
      tabsetPanel(
        tabPanel("Heart Disease", 
                 numericInput("age", "Age:", value = NA, min = 1, max = 120),
                 numericInput("sex", "Gender (1 = Male, 0 = Female):", value = NA, min = 0, max = 1),
                 numericInput("chesppain", "Chest Pain Type (1 to 4):", value = NA, min = 1, max = 4),
                 numericInput("restingbp", "Resting Blood Pressure:", value = NA),
                 numericInput("cholestrol", "Cholesterol Level:", value = NA),
                 numericInput("fastingbloodsugar", "Fasting Blood Sugar > 120 mg/dl (1 = Yes, 0 = No):", value = NA, min = 0, max = 1),
                 numericInput("electrocardiographic", "Resting Electrocardiographic Results (0, 1, 2):", value = NA),
                 numericInput("maxheartrate", "Maximum Heart Rate:", value = NA),
                 numericInput("exerciseangina", "Exercise Induced Angina (1 = Yes, 0 = No):", value = NA, min = 0, max = 1),
                 numericInput("oldpeak", "ST Depression (OldPeak):", value = NA),
                 numericInput("slopeofpeakexercise", "Slope of Peak Exercise (1 = Upsloping, 2 = Flat, 3 = Downsloping):", value = NA),
                 numericInput("ca", "Number of Major Vessels (0 to 3):", value = NA, min = 0, max = 3),
                 numericInput("thal", "Thalassemia (3 = Normal, 6 = Fixed Defect, 7 = Reversible Defect):", value = NA)
        ),
        tabPanel("Diabetes",
                 numericInput("pregnant", "Times Pregnant:", value = NA, min = 0),
                 numericInput("plasma", "Plasma Glucose:", value = NA),
                 numericInput("bp", "Diastolic Blood Pressure:", value = NA),
                 numericInput("tricep", "Tricep Skin Fold Thickness:", value = NA),
                 numericInput("insulin", "Serum Insulin:", value = NA),
                 numericInput("bmi", "Body Mass Index (BMI):", value = NA),
                 numericInput("pedigree", "Diabetes Pedigree Function:", value = NA),
                 numericInput("age_diabetes", "Age:", value = NA, min = 0)
        )
      ),
      actionButton("submit", "Submit", class = "btn-primary")
    ),
    
    mainPanel(
      h3("Prediction Result"),
      verbatimTextOutput("text"),
      br(),
      h4("Prediction Graph"),
      plotOutput("resultPlot")
    )
  )
)

# Define server logic
server <- function(input, output) {
  
  observeEvent(input$submit, {
    # Collect inputs for both models
    heart_input <- data.frame(
      Age = input$age,
      Sex = input$sex,
      chesp.pain.type = input$chesppain,
      resting.bp = input$restingbp,
      cholestrol = input$cholestrol,
      fasting.blood.sugar = input$fastingbloodsugar,
      electrocardiographic = input$electrocardiographic,
      maximum.heart.rate = input$maxheartrate,
      exercise.induced.angina = input$exerciseangina,
      oldpeak = input$oldpeak,
      slope.of.peak.exercise = input$slopeofpeakexercise,
      ca = input$ca,
      thal = input$thal
    )
    
    diabetes_input <- data.frame(
      times.pregnant = input$pregnant,
      plasma.glucose = input$plasma,
      diastolic.bp = input$bp,
      triceps.skin = input$tricep,
      serium.insuline = input$insulin,
      bmi = input$bmi,
      diabetes.pedigree = input$pedigree,
      age = input$age_diabetes
    )
    
    # Make predictions using the Naive Bayes models
    heart_prediction <- predict(heart_model, heart_input)
    diabetes_prediction <- predict(diabetes_model, diabetes_input)
    
    # Display prediction results
    output$text <- renderText({
      heart_pred <- ifelse(heart_prediction == 1, "Heart Disease", "No Heart Disease")
      diabetes_pred <- ifelse(diabetes_prediction == 1, "Diabetes", "No Diabetes")
      
      paste("Heart Disease Prediction: ", heart_pred, "\nDiabetes Prediction: ", diabetes_pred)
    })
    
    # Display prediction probabilities in a plot
    heart_prob <- predict(heart_model, heart_input, type = "raw")[1, 2] * 100
    diabetes_prob <- predict(diabetes_model, diabetes_input, type = "raw")[1, 2] * 100
    
    prediction_data <- data.frame(
      Disease = c("Heart Disease", "Diabetes"),
      Probability = c(heart_prob, diabetes_prob)
    )
    
    output$resultPlot <- renderPlot({
      ggplot(prediction_data, aes(x = Disease, y = Probability, fill = Disease)) +
        geom_bar(stat = "identity", width = 0.5) +
        geom_text(aes(label = paste(round(Probability, 2), "%")), vjust = -0.5) +
        theme_minimal() +
        labs(title = "Prediction Probability", x = "Disease", y = "Probability (%)")
    })
  })
}

# Run the application
shinyApp(ui = ui, server = server)

