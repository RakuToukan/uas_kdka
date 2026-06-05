package main

import (
    "github.com/gin-contrib/cors"
    "github.com/gin-gonic/gin"
    "github.com/r6rap/uas_kdka/api/handler"
    "time"
)

func main() {
    r := gin.Default()

    r.Use(cors.New(cors.Config{
        AllowOrigins:     []string{"*"},
        AllowMethods:     []string{"GET", "POST", "OPTIONS"},
        AllowHeaders:     []string{"Origin", "Content-Type", "ngrok-skip-browser-warning"},
        ExposeHeaders:    []string{"Content-Length", "Content-Type"},
        MaxAge:           12 * time.Hour,
    }))

    r.GET("/categories", handler.GetCategories)
    r.GET("/distances", handler.GetDistance)
    r.POST("/mosaic", handler.PostMosaic)
    r.GET("/status/:id", handler.GetStatus)

    r.Run(":8080")
}