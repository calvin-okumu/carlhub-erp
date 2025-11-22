"use client";

import React, { useState } from 'react';
import { ChevronDown, LucideIcon } from 'lucide-react';

interface SelectOption {
  value: string;
  label: string;
  icon?: LucideIcon;
  description?: string;
  color?: string;
}

interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'onChange'> {
  className?: string;
  options?: SelectOption[];
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  showIcons?: boolean;
}

export default function Select({ 
  className = '', 
  options = [],
  value,
  onChange,
  placeholder = 'Select an option',
  showIcons = true,
  ...props 
}: SelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);

  // If no options provided, use as regular select
  if (options.length === 0) {
    return (
      <select
        {...props}
        className={`w-full p-3 border border-gray-300 bg-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ${className}`}
      />
    );
  }

  const selectedOption = options.find(option => option.value === value);

  const handleSelect = (optionValue: string) => {
    onChange?.(optionValue);
    setIsOpen(false);
    setHighlightedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (isOpen && highlightedIndex >= 0) {
        handleSelect(options[highlightedIndex].value);
      } else {
        setIsOpen(!isOpen);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setIsOpen(true);
      setHighlightedIndex(prev => 
        prev < options.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setIsOpen(true);
      setHighlightedIndex(prev => 
        prev > 0 ? prev - 1 : options.length - 1
      );
    } else if (e.key === 'Escape') {
      setIsOpen(false);
      setHighlightedIndex(-1);
    }
  };

  return (
    <div className={`relative ${className}`}>
      <div
        className={`w-full p-3 border border-gray-300 bg-white rounded-lg cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 flex items-center justify-between ${
          isOpen ? 'ring-2 ring-blue-500 border-transparent' : 'hover:border-gray-400'
        }`}
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        tabIndex={0}
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-controls="select-listbox"
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {selectedOption?.icon && showIcons && (
            <selectedOption.icon className="w-5 h-5 text-gray-500 flex-shrink-0" />
          )}
          <div className="min-w-0 flex-1">
            <div className="text-gray-900 font-medium truncate">
              {selectedOption?.label || placeholder}
            </div>
            {selectedOption?.description && (
              <div className="text-sm text-gray-500 truncate">
                {selectedOption.description}
              </div>
            )}
          </div>
        </div>
        <ChevronDown 
          className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${
            isOpen ? 'transform rotate-180' : ''
          }`} 
        />
      </div>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
          {options.map((option, index) => (
            <div
              key={option.value}
              className={`px-3 py-2 cursor-pointer transition-colors duration-150 flex items-center gap-3 ${
                index === highlightedIndex 
                  ? 'bg-blue-50 text-blue-900' 
                  : 'hover:bg-gray-50 text-gray-900'
              } ${option.value === value ? 'bg-blue-50 text-blue-900 font-medium' : ''}`}
              onClick={() => handleSelect(option.value)}
              role="option"
              aria-selected={option.value === value}
            >
              {option.icon && showIcons && (
                <option.icon 
                  className={`w-5 h-5 flex-shrink-0 ${
                    option.color ? `text-${option.color}-500` : 'text-gray-500'
                  }`} 
                />
              )}
              <div className="min-w-0 flex-1">
                <div className="font-medium truncate">{option.label}</div>
                {option.description && (
                  <div className="text-sm text-gray-500 truncate">
                    {option.description}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}