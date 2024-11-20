export class Project {
  constructor({
    id = crypto.randomUUID(),
    name,
    type,
    location,
    startDate,
    status = 'PLANNING'
  }) {
    this.id = id;
    this.name = name;
    this.type = type;
    this.location = location;
    this.startDate = startDate;
    this.status = status;
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  update(updates) {
    Object.assign(this, updates);
    this.updatedAt = new Date();
  }
}
