package handler

import (
	"net/http"
	"github.com/gin-gonic/gin"
)

var availableDistance = []string{"euclidean", "minkowski"}

func GetDisrance(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"distance": availableDistance,
	})
}