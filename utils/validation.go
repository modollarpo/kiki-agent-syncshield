package utils

import (
	"github.com/go-playground/validator/v10"
)

var validate = validator.New()

type ValidationError struct {
	Field string
	Tag   string
	Value interface{}
}

func ValidateStruct(s interface{}) []*ValidationError {
	err := validate.Struct(s)
	if err == nil {
		return nil
	}
	var errors []*ValidationError
	for _, err := range err.(validator.ValidationErrors) {
		e := &ValidationError{
			Field: err.Field(),
			Tag:   err.Tag(),
			Value: err.Value(),
		}
		errors = append(errors, e)
	}
	return errors
}
