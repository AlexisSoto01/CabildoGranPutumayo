$(document).ready(function() {
  $('.miTabla').DataTable({
      "language": {
          "url": "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
      }
  });

  $('#select-field2').select2({
      theme: "bootstrap-5",
      width: $(this).data('width') ? $(this).data('width') : $(this).hasClass('w-100') ? '100%' : 'style',
      placeholder: $(this).data('placeholder'),
      closeOnSelect: false,
  });

  $('.btn-dlt').on('click', function() {
      var entityType = $(this).data('type'); 
      var entityId = $(this).data('pk'); 
      var entityName = $(this).data('name');

      $('#entityType').text(entityType.replace('_', ' ').charAt(0).toUpperCase() + entityType.slice(1)); 
      $('#entityName').text(entityName);

      var deleteUrl;
      if (entityType === 'usuario') {
          deleteUrl = `/user/${entityId}/delete/`;
      } else if (entityType === 'familia') {
          deleteUrl = `/families/${entityId}/delete/`;
      } else if (entityType === 'evento') {
          deleteUrl = `/event/${entityId}/delete/`;
      } else if (entityType === 'usuario_familia') {
          deleteUrl = `/user/family/${entityId}/delete/`;
      } else if (entityType === 'usuario_evento') {
          deleteUrl = `/user/events/${entityId}/delete/`;
      }

      $('#confirmDeleteButton').attr('href', deleteUrl);

      $('#deleteModal').modal('show');
  });

  setTimeout(function () {
      $(".alert").fadeOut("slow", function () {
          $(this).remove(); 
      });
  }, 5000);
});
