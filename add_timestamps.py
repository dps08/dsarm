#!/usr/bin/env python3
"""
Add timestamp tracking to the roadmap
"""

import re

# Read the current HTML
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update all table headers to include "Completed" column
html = re.sub(
    r'<th width="5%">✓</th>',
    '<th width="3%">✓</th>\n                            <th width="12%">Completed</th>',
    html
)

# 2. Add data-day attributes and completion date cells to all checkboxes
day_counter = 1
lines = html.split('\n')
new_lines = []

for i, line in enumerate(lines):
    if '<td><input type="checkbox" class="day-complete"></td>' in line:
        # Add data-day attribute to checkbox and add completion date cell
        new_line = f'                            <td><input type="checkbox" class="day-complete" data-day="{day_counter}"></td>'
        new_lines.append(new_line)
        new_lines.append(f'                            <td class="completion-date" data-day="{day_counter}">-</td>')
        day_counter += 1
    else:
        new_lines.append(line)

html = '\n'.join(new_lines)

# 3. Add CSS for the completion date column
css_addition = """
        .completion-date {
            font-size: 11px;
            color: var(--text-secondary);
            font-family: 'JetBrains Mono', monospace;
        }
        
        .completion-date.completed {
            color: var(--success);
            font-weight: 500;
        }
"""

html = html.replace('        .hidden {', css_addition + '        .hidden {')

# 4. Update JavaScript to track timestamps
js_update = """
        // Update progress tracking
        function updateProgress() {
            const checkboxes = document.querySelectorAll('.day-complete:checked').length;
            const totalBoxes = document.querySelectorAll('.day-complete').length;
            const percentage = Math.round((checkboxes / totalBoxes) * 100);
            
            progressBar.style.width = percentage + '%';
            progressBar.textContent = percentage + '%';
            
            // Update counters
            daysCount.textContent = checkboxes + '/90';
            
            // Estimate problems solved (roughly 5 per day average)
            const estimatedProblems = Math.round(checkboxes * 5.2);
            problemsCount.textContent = estimatedProblems + '/465';
            
            // Update phase
            if (checkboxes <= 30) {
                currentPhase.textContent = 'Phase 1: Foundation';
            } else if (checkboxes <= 60) {
                currentPhase.textContent = 'Phase 2: Intermediate';
            } else {
                currentPhase.textContent = 'Phase 3: Advanced';
            }
            
            // Save to localStorage with timestamps
            const completedDays = {};
            document.querySelectorAll('.day-complete').forEach(cb => {
                const day = cb.dataset.day;
                if (cb.checked) {
                    const savedData = JSON.parse(localStorage.getItem('roadmap-progress') || '{}');
                    if (!savedData.timestamps || !savedData.timestamps[day]) {
                        // New completion - save current timestamp
                        completedDays[day] = new Date().toISOString();
                    } else {
                        // Already completed - keep existing timestamp
                        completedDays[day] = savedData.timestamps[day];
                    }
                }
            });
            
            localStorage.setItem('roadmap-progress', JSON.stringify({
                checked: Array.from(document.querySelectorAll('.day-complete')).map(cb => cb.checked),
                timestamps: completedDays,
                date: new Date().toISOString()
            }));
            
            // Update completion date displays
            updateCompletionDates();
        }
        
        // Update completion date displays
        function updateCompletionDates() {
            const savedData = JSON.parse(localStorage.getItem('roadmap-progress') || '{}');
            const timestamps = savedData.timestamps || {};
            
            document.querySelectorAll('.completion-date').forEach(cell => {
                const day = cell.dataset.day;
                if (timestamps[day]) {
                    const date = new Date(timestamps[day]);
                    const formatted = date.toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    cell.textContent = formatted;
                    cell.classList.add('completed');
                } else {
                    cell.textContent = '-';
                    cell.classList.remove('completed');
                }
            });
        }
        
        // Load saved progress with timestamps
        const savedProgress = localStorage.getItem('roadmap-progress');
        if (savedProgress) {
            const data = JSON.parse(savedProgress);
            checkboxes.forEach((cb, index) => {
                cb.checked = data.checked[index] || false;
            });
            updateProgress();
            updateCompletionDates();
        }
"""

# Find and replace the updateProgress function
pattern = r'// Update progress tracking.*?// Save to localStorage\s+localStorage\.setItem\([^)]+\);[^}]*}'
html = re.sub(pattern, js_update, html, flags=re.DOTALL)

# Write the updated HTML
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully added date/time tracking to the roadmap!")