import { useState } from 'react';

export const useTableSelection = <T extends { id: string }>(items: T[] = []) => {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const isSelected = (id: string) => selectedIds.includes(id);
  const isAllSelected = items.length > 0 && selectedIds.length === items.length;
  const isSomeSelected = selectedIds.length > 0 && selectedIds.length < items.length;

  const toggleSelect = (id: string) => {
    setSelectedIds(prev =>
      prev.includes(id)
        ? prev.filter(selectedId => selectedId !== id)
        : [...prev, id]
    );
  };

  const selectAll = (checked: boolean) => {
    setSelectedIds(checked ? items.map(item => item.id) : []);
  };

  const clearSelection = () => setSelectedIds([]);

  const selectedCount = selectedIds.length;

  return {
    selectedIds,
    isSelected,
    isAllSelected,
    isSomeSelected,
    toggleSelect,
    selectAll,
    clearSelection,
    selectedCount
  };
};