import { AfterViewInit, Component, ViewChild } from '@angular/core';
import { MatTableModule, MatTable } from '@angular/material/table';
import { MatPaginatorModule, MatPaginator } from '@angular/material/paginator';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MoviesTableDataSource } from './movies-table-datasource';
import { Movie, MoviesService } from '../movies.service';
import { MatFormField } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';   


@Component({
    selector: 'app-movies-table',
    templateUrl: './movies-table.component.html',
    styleUrl: './movies-table.component.css',
    standalone: true,
    imports: [MatTableModule, MatPaginatorModule, MatSortModule, MatFormField, MatInputModule ]
})
export class MoviesTableComponent implements AfterViewInit {
    @ViewChild(MatPaginator) paginator!: MatPaginator;
    @ViewChild(MatSort) sort!: MatSort;
    @ViewChild(MatTable) table!: MatTable<Movie>;
    dataSource!: MoviesTableDataSource;

    constructor(service: MoviesService) {
        this.dataSource = new MoviesTableDataSource(service);
    }
    displayedColumns = ['title', 'year', 'studio', 'director'];

    ngAfterViewInit(): void {
        this.dataSource.sort = this.sort;
        this.dataSource.paginator = this.paginator;
        this.table.dataSource = this.dataSource;
    }

    applyFilter(event: Event) {
        const filterValue = (event.target as HTMLInputElement).value;
        this.dataSource.filter = filterValue.trim().toLowerCase();
        this.dataSource.filterChange.emit(filterValue);
        console.log(this.dataSource.filter);
        if (this.dataSource.paginator) {
            this.dataSource.paginator.firstPage();
        }
    }
}
