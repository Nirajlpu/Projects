
library(shiny)
library(shinydashboard)
library(ggplot2)
library(dplyr)
library(leaflet)

set.seed(123)
traffic_data <- data.frame(
  location = c("New Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Ahmedabad", "Pune", "Surat", "Jaipur"),
  vehicle_count = sample(100:500, 10),
  avg_speed = sample(20:60, 10),
  congestion_level = sample(c("High", "Medium", "Low"), 10, replace = TRUE),
  latitude = c(28.6139, 19.0760, 12.9716, 13.0827, 22.5726, 17.3850, 23.0225, 18.5204, 21.1702, 26.9124),
  longitude = c(77.2090, 72.8777, 77.5946, 80.2707, 88.3639, 78.4867, 72.5714, 73.8567, 72.8310, 75.8243)
)

ui <- dashboardPage(
  dashboardHeader(title = "Traffic Management Dashboard"),
  dashboardSidebar(
    sidebarMenu(
      menuItem("Overview", tabName = "overview", icon = icon("dashboard")),
      menuItem("Detailed Analysis", tabName = "analysis", icon = icon("chart-line")),
      menuItem("Congestion Hotspots", tabName = "hotspots", icon = icon("map"))
    )
  ),
  dashboardBody(
    tabItems(

      tabItem(tabName = "overview",
              fluidRow(
                box(
                  title = "Total Vehicle Count",
                  width = 3,
                  background = "blue",
                  textOutput("total_vehicles")
                ),
                box(
                  title = "Average Speed",
                  width = 3,
                  background = "green",
                  textOutput("avg_speed")
                ),
                box(
                  title = "Congestion Levels",
                  width = 3,
                  background = "orange",
                  textOutput("congestion")
                ),
                box(
                  title = "Locations",
                  width = 3,
                  background = "purple",
                  textOutput("locations")
                )
              ),
              fluidRow(
                box(
                  title = "High Traffic Photo(Vikas Marg,Delhi)",
                  width = 6,
                  imageOutput("high_traffic_photo")
                ),
                box(
                  title = "High Traffic Video(Vikas Marg,Delhi)",
                  width = 6,
                  tags$video(
                    src = "/Users/nirajkumar/trafficVideo.mp4",
                    type = "video/mp4",
                    controls = TRUE,
                    width = "100%",
                    height = "auto"
                  )
                )
              ),
              fluidRow(
                box(
                  title = "New Delhi",
                  width = 3,
                  imageOutput("image1")
                ),
                box(
                  title = "Mumbai",
                  width = 3,
                  imageOutput("image2")
                ),
                box(
                  title = "Bangalore",
                  width = 3,
                  imageOutput("image3")
                ),
                box(
                  title = "Chennai",
                  width = 3,
                  imageOutput("image4")
                )
              )
      ),

      tabItem(tabName = "analysis",
              fluidRow(
                box(
                  title = "Vehicle Count by Location",
                  width = 6,
                  plotOutput("vehicle_count_plot")
                ),
                box(
                  title = "Average Speed by Location",
                  width = 6,
                  plotOutput("avg_speed_plot")
                )
              )
      ),

      tabItem(tabName = "hotspots",
              fluidRow(
                box(
                  title = "Congestion Hotspot Map",
                  width = 12,
                  leafletOutput("congestion_map")
                )
              )
      )
    )
  )
)


server <- function(input, output) {
  # Overview tab outputs
  output$total_vehicles <- renderText({
    sum(traffic_data$vehicle_count)
  })
  output$avg_speed <- renderText({
    round(mean(traffic_data$avg_speed), 2)
  })
  output$congestion <- renderText({
    paste(unique(traffic_data$congestion_level), collapse = ", ")
  })
  output$locations <- renderText({
    paste(traffic_data$location, collapse = ", ")
  })
  
  output$high_traffic_photo <- renderImage({

    list(src = "/Users/nirajkumar/Desktop/R-based-dashboard-traffic-management/trafficImage.jpeg",
         alt = "High Traffic Photo")
  }, deleteFile = FALSE)
  

  output$image1 <- renderImage({
    list(src = "/Users/nirajkumar/Desktop/R-based-dashboard-traffic-management/traffic1.jpeg",
         alt = "Traffic Image 1")
  }, deleteFile = FALSE)
  

  output$image2 <- renderImage({
    list(src = "/Users/nirajkumar/Desktop/R-based-dashboard-traffic-management/traffic2.jpeg",
         alt = "Traffic Image 2")
  }, deleteFile = FALSE)
  

  output$image3 <- renderImage({
    list(src = "/Users/nirajkumar/Desktop/R-based-dashboard-traffic-management/traffic3.jpeg",
         alt = "Traffic Image 3")
  }, deleteFile = FALSE)
  

  output$image4 <- renderImage({
    list(src = "/Users/nirajkumar/Desktop/R-based-dashboard-traffic-management/traffic4.jpeg",
         alt = "Traffic Image 4")
  }, deleteFile = FALSE)
  

  output$vehicle_count_plot <- renderPlot({
    ggplot(traffic_data, aes(x = location, y = vehicle_count, fill = location)) +
      geom_bar(stat = "identity") +
      labs(x = "Location", y = "Vehicle Count", fill = "Location") +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 45, hjust = 1))
  })
  
  output$avg_speed_plot <- renderPlot({
    ggplot(traffic_data, aes(x = location, y = avg_speed, fill = location)) +
      geom_bar(stat = "identity") +
      labs(x = "Location", y = "Average Speed", fill = "Location") +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 45, hjust = 1))
  })
  

  output$congestion_map <- renderLeaflet({
    leaflet(traffic_data) %>%
      addTiles() %>%
      addMarkers(
        ~longitude, ~latitude,
        popup = ~paste0("Location: ", location, "<br>",
                        "Vehicle Count: ", vehicle_count, "<br>",
                        "Average Speed: ", avg_speed, "<br>",
                        "Congestion Level: ", congestion_level),
        label = ~location,
        icon = ~makeIcon(
          iconUrl = case_when(
            congestion_level == "High" ~ "https://via.placeholder.com/15/ff0000/000000?text=H",
            congestion_level == "Medium" ~ "https://via.placeholder.com/15/ffa500/000000?text=M",
            congestion_level == "Low" ~ "https://via.placeholder.com/15/00ff00/000000?text=L"
          ),
          iconWidth = 20, iconHeight = 20
        )
      ) %>%
      addLegend(
        pal = colorFactor(c("red", "orange", "green"), domain = c("High", "Medium", "Low")),
        values = ~congestion_level,
        title = "Congestion Level"
      )
  })
}


shinyApp(ui, server)
