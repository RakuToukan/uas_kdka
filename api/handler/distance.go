package handler

import (
	"net/http"
	"github.com/gin-gonic/gin"
)

var availableDistance = []string{"euclidean", "minkowski", "manhattan"}

func GetDistance(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"distance": availableDistance,
	})
}